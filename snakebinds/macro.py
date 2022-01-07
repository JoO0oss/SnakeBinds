"""Contains most of the macro-running juice, it creates, starts and stops all threading required to use macros."""
from typing import Union, List, Dict, Tuple, Set, Callable
import threading
import time
from pynput import mouse, keyboard
from snakebinds.snakebind_pynput import lookup_bind
import Xlib.threaded  # "Temporarily" added by Joss according to https://stackoverflow.com/questions/20872826/pyuserinput-and-xlib-crashing

currently_held_keys: List[keyboard.Key] = []
KEY_WARN = False
DEBUG_SHOW_KEYS = False
_run = False


class MacroThread:
    """Wraps a function, runs it as a thread, and says whether the macro has finished."""
    def __init__(self, func: Callable):
        self._finished: bool = False
        self._killable: bool = False
        self._thread: Union[threading.Thread, None] = None

        def run_this():
            nonlocal self
            func()
            self._finished = True

        self._run_this: Callable = run_this

    @property
    def finished(self) -> bool:
        """Returns whether the function has finished executing."""
        return self._finished

    @property
    def killable(self) -> bool:
        """Returns whether the object can be removed."""
        return self._killable

    def start(self):
        """Starts running the code in the macro. Errors if it has already started."""
        if self._thread is not None:
            raise RuntimeError("Macro thread has already started running.")

        self._thread = threading.Thread(target=self._run_this)
        self._thread.start()

    def stop(self):
        """Finishes the thread and makes it killable. Errors if function still running."""
        if not self._finished:
            raise RuntimeError("Tried to stop a macro thread while still running.")

        if self._thread is None:
            raise RuntimeError("Thread has not been started yet.")

        self._thread.join()
        self._killable = True


_bound_keys: Dict[Tuple[str], Callable] = {}  # User defined macro combinations and their respective functions.
_run_these_funcs: List[Callable] = []  # This stores scheduled macros to run.
_macro_threads: List[MacroThread] = []  # These are the running macros.


def false_if_exclamation(word: str) -> bool:
    """Return True if the word does not start with !."""
    return word[0] != "!"


def is_not_killable(macro_thread: MacroThread) -> bool:
    return not macro_thread.killable


def get_inclusions(key_names: Tuple[str]) -> Set[str]:
    """Returns all required keys pressed for this macro to trigger."""
    return set(filter(false_if_exclamation, key_names))


def get_exclusions(key_names: Tuple[str]) -> Set[str]:
    """Returns all required keys unpressed for this macro to trigger."""
    exclusions = []
    for key_name in key_names:
        if key_name[0] == "!":
            exclusions.append(key_name[1:])

    return set(exclusions)


def convert_key(key: Union[keyboard.Key, keyboard.KeyCode, mouse.Button]) -> str:
    """Converts a pynput key object to a string."""
    if isinstance(key, mouse.Button):
        return "mouse_" + key.name

    if hasattr(key, "name"):
        return key.name
    else:
        return str(key).lower().replace("'", "")


def try_hotkey(pressed_keys: List[Union[keyboard.Key, keyboard.KeyCode, mouse.Button]]):
    """Submit a combination of key presses here and this will sort scheduling necessary macros."""

    pressed_keys_strs: Set[str] = {convert_key(key) for key in pressed_keys}
    if DEBUG_SHOW_KEYS:
        print(pressed_keys_strs)

    # Look through bound macros to see if they need running.
    for key_combination in _bound_keys:
        required_inclusions = get_inclusions(key_combination)

        # First check if all required inclusions of a bound macro are met.
        if required_inclusions.issubset(pressed_keys_strs):
            required_exclusions = get_exclusions(key_combination)

            # Then check that there is no overlap between pressed keys and banned keys.
            if required_exclusions.intersection(pressed_keys_strs) == set():

                # If all required keys are pressed, and banned keys are unpressed, then schedule the function.
                global _run_these_funcs
                _run_these_funcs.append(_bound_keys[key_combination])


def on_click(x: int, y: int, button: mouse.Button, pressed: bool):
    """This function runs code every time the user clicks.

    Arguments:
        x: The x position of received click event.
        y: The y position of received click event.
        button: which button this event is about.
        pressed: True if it was a button down event, False if it was button up.

    """
    if pressed:
        if button not in currently_held_keys:
            currently_held_keys.append(button)
        else:
            if KEY_WARN:
                print(f"WARNING: {button} pressed despite prior pressed status.")

    else:
        try:
            currently_held_keys.remove(button)
        except ValueError:
            if KEY_WARN:
                print(f"WARNING: {button} released without prior pressed status.")

    try_hotkey(currently_held_keys)


def on_press(key: keyboard.Key):
    """This function runs code every time the user pushes a key down on the keyboard.

    Arguments:
        key: The type of key pressed.

    """
    if _run:
        if key not in currently_held_keys:
            currently_held_keys.append(key)
        else:
            if KEY_WARN:
                print(f"WARNING: {key} pressed despite prior pressed status.")

    try_hotkey(currently_held_keys)


def on_release(key: keyboard.Key):
    """This function runs code every time the user lifts a key on the keyboard.

    Arguments:
        key: The type of key released.

    """

    if _run:
        try:
            currently_held_keys.remove(key)
        except ValueError:
            if KEY_WARN:
                print(f"WARNING: {key} released without prior pressed status.")


def bind(*funcs: Callable):
    """Give this all macro functions, and it will automatically run them when the key combination specified in the
    docstring is pressed.

    Arguments:
        funcs: a list of macro functions whose key combination is written in the docstring.

    Raises:
        ValueError: if the string specifying the macro is not valid.
        NameError: if the macro key combination is already in use.
    """
    global _run
    global _bound_keys
    global _run_these_funcs

    _run = True

    for func in funcs:
        keyname_list: List[str] = []
        for keyname in func.__doc__.replace(" ", "").split("+"):
            key_lookup = lookup_bind(keyname.lower())
            if key_lookup is None:
                raise ValueError(f"{repr(keyname)} ({func.__doc__}) is not a valid pynput identifier or snakebinds alias.")

            keyname_list.append(lookup_bind(keyname.lower()))

        keyname_tuple = tuple(keyname_list)
        if keyname_tuple in _bound_keys:
            raise NameError(f"{'+'.join(keyname_tuple)} already defines a macro.")
        _bound_keys[keyname_tuple] = func

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    def event_loop():
        global _macro_threads
        while _run:
            time.sleep(0.001)
            while len(_run_these_funcs) > 0:
                cur_func = _run_these_funcs[0]

                _macro_threads.append(MacroThread(cur_func))
                _macro_threads[-1].start()
                del _run_these_funcs[0]  # Remove functions as they are dealt with.

            if len(_macro_threads) > 0:
                for i, macro_thread in enumerate(_macro_threads):
                    if macro_thread.finished:
                        macro_thread.stop()

                _macro_threads = list(filter(is_not_killable, _macro_threads))  # Remove all killable macro threads.


    event_thread = threading.Thread(target=event_loop)
    event_thread.start()
    event_thread.join()


def unbind():
    """Essentially stop function. It prevents starting any new macros without exiting the program."""
    global _run
    _run = False
