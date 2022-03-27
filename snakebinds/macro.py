"""Contains most of the macro-running juice, it creates, starts and stops all threading required to use macros."""
from typing import Callable
import threading
import time
from pynput import mouse, keyboard

from snakebinds.snakebind_pynput import alias_to_snakebind, pynput_to_snakebind


KEY_WARN = False  # Alerts if a key event triggers changing it to a state it's already in.
DEBUG_SHOW_KEYS = False  # Prints keypress events to the console.


class bind:
    """Decorator for creating a new macro."""
    def __init__(self, func=None, args=[], kwargs={}):
        # Doing this means you can call bind() as a normal function, *or* wrap a function as a decorator.
        if func is None:
            # Usage as a function to call to start running macros.
            _bind()
        
        else:
            bind_this_function(func)

class MacroThread:
    """Wraps a function, runs it as a thread, and says whether the macro has finished."""
    def __init__(self, func: Callable, *args, **kwargs):
        self._started = False
        self._finished = False
        self._killable = False

        def run_this():
            nonlocal self
            func()
            self._finished = True
        
        self._thread = threading.Thread(target=run_this, args=args, kwargs=kwargs)

    @property
    def started(self) -> bool:
        return self._started
    
    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def killable(self) -> bool:
        return self._killable

    def start(self):
        """Starts running the code in the macro. Errors if it has already started."""
        if self._started:
            raise RuntimeError("Macro thread has already started.")
        
        self._started = True
        self._thread.start()

    # The reason this is here is so that the thread can notify the outer program that it has
    # finished without twisting around trying to join itself from within the thread.
    def stop(self):
        """Finishes the thread and makes it killable. Errors if function still running."""
        if not self._finished:
            # This bit detects whether the inner thread has yet told the outer program it has finished.
            raise RuntimeError("Tried to stop a macro thread while still running.")

        if not self._started:
            raise RuntimeError("Thread has not been started yet.")

        self._thread.join()
        self._killable = True


_run = False
_bound_keys: dict[tuple[str], Callable] = {}  # User defined macro combinations and their respective functions.
_pressed_keys: dict[tuple[str], bool] = {}

_run_these_funcs: list[Callable] = []  # This stores scheduled macros to run.
_currently_held_keys: set[str] = set()
_macro_threads: list[MacroThread] = []  # These are the running macros.


def false_if_exclamation(word: str) -> bool: return word[0] != "!"
def is_not_killable(macro_thread: MacroThread) -> bool: return not macro_thread.killable

# These two functions separate required keys pressed from required !keys unpressed.
def get_inclusions(key_names: tuple[str]) -> set[str]:
    """Returns all required keys pressed for this macro to trigger. Doesn't return !keys."""
    return set(filter(false_if_exclamation, key_names))

def get_exclusions(key_names: tuple[str]) -> set[str]:
    """Returns all required !keys unpressed for this macro to trigger."""
    exclusions = []
    for key_name in key_names:
        if key_name[0] == "!":
            exclusions.append(key_name[1:])

    return set(exclusions)

# Runs every time an event is received.
def try_hotkey(currently_held_keys: list[keyboard.Key | keyboard.KeyCode | mouse.Button]):
    """Checks if the current combination of keys is a hotkey, and schedules it to run if so.

    Arguments:
        currently_held_keys: The keys currently held down.
    """
    global _run_these_funcs  # Not necessary, but I prefer explicitly showing it's global.
    global _bound_keys
    global _pressed_keys

    if DEBUG_SHOW_KEYS:
        print(f"Currently held keys: {currently_held_keys}")

    if _run:  # Don't try to add new macros when the program is idle.
        for key_comb in _bound_keys:

            # Make sure all keys in the combination are pressed.
            if get_inclusions(key_comb) <= currently_held_keys:

                # Make sure no !keys are pressed.
                if not get_exclusions(key_comb) & currently_held_keys:

                    # Make sure this only occurs once per key combination.
                    if not _pressed_keys[key_comb]:
                        _run_these_funcs.append(_bound_keys[key_comb])
                        _pressed_keys[key_comb] = True
                else:
                    _pressed_keys[key_comb] = False
            
            else:
                _pressed_keys[key_comb] = False  # Update that it's not pressed *after* trying to trigger the functions.


# This just exists so the program recognises when keys are unpressed, without having to trigger hotkeys again.
def untry_hotkey(currently_held_keys: list[keyboard.Key | keyboard.KeyCode | mouse.Button]):
    """Checks if the current combination of keys is a hotkey, but doesn't run anything.

    Arguments:
        currently_held_keys: The keys currently held down.
    """
    global _pressed_keys

    for key_comb in _pressed_keys:
        if get_inclusions(key_comb) <= currently_held_keys:
            if not get_exclusions(key_comb) & currently_held_keys:
                    _pressed_keys[key_comb] = True
            else:
                _pressed_keys[key_comb] = False
        else:
            _pressed_keys[key_comb] = False


# These three functions are the pynput event listeners.
def on_click(x: int, y: int, button: mouse.Button, pressed: bool):
    """This function runs code every time the user clicks.

    Arguments:
        x: The x position of received click event.
        y: The y position of received click event.
        button: which button this event is about.
        pressed: True if it was a button down event, False if it was button up.

    """
    global _currently_held_keys

    key_str = pynput_to_snakebind(button)
    if pressed:
        if button not in _currently_held_keys:
            _currently_held_keys |= {key_str}
        else:
            if KEY_WARN:
                print(f"WARNING: {key_str} pressed despite prior pressed status.")
        
        try_hotkey(_currently_held_keys)  # Don't check on release since that could complicate things for the user.

    else:
        try:
            _currently_held_keys -= {key_str}
        except ValueError:
            if KEY_WARN:
                print(f"WARNING: {key_str} released without prior pressed status.")

def on_press(key: keyboard.Key):
    """This function runs code every time the user pushes a key down on the keyboard.

    Arguments:
        key: The type of key pressed.

    """
    global _currently_held_keys
    
    key_str = pynput_to_snakebind(key)
    if _run:
        if key not in _currently_held_keys:
            _currently_held_keys |= {key_str}
        else:
            if KEY_WARN:
                print(f"WARNING: {key_str} pressed despite prior pressed status.")

    try_hotkey(_currently_held_keys)

def on_release(key: keyboard.Key):
    """This function runs code every time the user lifts a key on the keyboard.

    Arguments:
        key: The type of key released.

    """
    global _currently_held_keys
    
    key_str = pynput_to_snakebind(key)
    if _run:
        try:
            _currently_held_keys -= {key_str}
        except ValueError:
            if KEY_WARN:
                print(f"WARNING: {key_str} released without prior pressed status.")
    
    untry_hotkey(_currently_held_keys)
    # Don't try to check for hotkeys being pressed, otherwise the user would have to focus
    # carefully on which order they release keys from other macros.


def bind_this_function(new_func: Callable):
    """Takes a function and binds the key combination to running said function.

    Arguments:
        new_func:
            The function to be added to the list of macros.
            It must have a docstring, which is used to create the macro.
    
    Raises: NameError if the key combination is already bound.
    """
    keyname_list: list[str] = []  # List of keys that need to be pressed to run the macro code.

    macro_str: str = new_func.__doc__
    macro_str = macro_str.replace(" ", "")

    # If there is no docstring, then it shouldn't try to be a macro.
    if macro_str == "":
        raise ValueError(f"Tried to bind {new_func.__name__} without macro definition.")

    macro_keys = macro_str.split("+")

    for keyname in macro_keys:
        # Ignore case for all macro strings.
        key_lookup = alias_to_snakebind(keyname.lower())  # Convert aliases here.
        if key_lookup is None:
            raise ValueError(f"{repr(keyname)} (macro_str) is not a valid pynput identifier or snakebinds alias.")

        keyname_list.append(key_lookup)

    keyname_tuple = tuple(keyname_list)  # Use a tuple so it's hashable for a dictionary.
    if keyname_tuple in _bound_keys:
        raise NameError(f"{new_func.__doc__} already defines a macro.")
    _bound_keys[keyname_tuple] = new_func  # new_func will now run when the key combination is pressed.
    _pressed_keys[keyname_tuple] = False  # Initialize the pressed keys to false.


def unbind():
    """Run this to stop checking for macro combinations being pressed."""
    global _run
    _run = False

def rebind():
    """Run this to start/restart checking for macro combinations being pressed."""
    global _run
    _run = True

    def event_loop():
        global _macro_threads
        while _run:
            time.sleep(0.01)
            while _run_these_funcs:
                cur_func = _run_these_funcs.pop(0)  # Take the functions off the list and queue them to run.
                _macro_threads.append(MacroThread(cur_func))
                _macro_threads[-1].start()

                for thread in _macro_threads:
                    if thread.finished:
                        thread.stop()  # This bit makes it killable.
                
                _macro_threads = list(filter(is_not_killable, _macro_threads))  # Remove finished threads.
    
    event_thread = threading.Thread(target=event_loop)
    event_thread.start()
    event_thread.join()  # You can't accidentally try to run rebind() in your code and screw things over because this bit hangs until loose ends are tied up.

# Called when the program is first started, run by bind class __init__ to reduce namespace clutter.
def _bind():
    """Initialise listeners then start checking for macro combinations being pressed."""
    global _run
    global _bound_keys
    global _run_these_funcs
    
    _run = True

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    # Start checking for macro combinations in here.
    rebind()

# Just so the user doesn't need to track whether it's paused in their scripts.
def is_running():
    """Shows whether macros are running or not."""
    global _run
    return _run
