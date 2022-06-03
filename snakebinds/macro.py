from __future__ import annotations

"""Contains most of the macro-running juice, it creates, starts and stops all threading required to use macros."""
from typing import Callable
import threading
import time
from pynput import mouse, keyboard
from functools import partial
import pyautogui
from snakebinds.snakebind_pynput import alias_to_snakebind, pynput_to_snakebind, os


def bind(func=None):
    """Decorator for creating a new macro.
    Alternatively call in isolation to start running macros.

    Arguments:
        func: The function to run when the macro is triggered, leave blank to start off the
            background macro detection and running.
    Returns:
        func, unmodified.
    """
    # Doing this means you can call bind() as a normal function, *or* wrap a function as a decorator.
    if func is None:
        # Usage as a function to call to start running macros.
        _bind()
    
    else:
        bind_this_function(func)
    
    return func  # Don't otherwise modify the code around the functions.


class MacroThread:
    """Wraps a function, runs it as a thread, and says whether the macro has finished."""
    def __init__(self, func: Callable, *args, **kwargs):
        self._started = False
        self._finished = False
        self._killable = False

        def run_this():
            nonlocal self
            try:
                func()
            finally:
                # Make sure that even if func() errors, the thread can still be joined.
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
_pressed_keys: dict[tuple[str], bool] = {}  # This prevents a macro running more than once at a time.

_run_these_funcs: list[Callable] = []  # This stores scheduled macros to run.
_currently_held_keys: set[str] = set()
_macro_threads: list[MacroThread] = []  # These are the running macros.
_queued_partials: list[Callable] = []  # Invidividual keys are pressed as per their position in this queue.


def false_if_exclamation(word: str) -> bool: return word[0] != "!"
def is_not_killable(macro_thread: MacroThread) -> bool: return not macro_thread.killable
def stop_if_finished(macro_thread: MacroThread):
    if macro_thread.finished:
        macro_thread.stop()

# These two functions separate required keys pressed from required !keys unpressed.
def get_inclusions(key_names: tuple[str]) -> set[str]:
    """Returns all required keys pressed for this macro to trigger. Doesn't return !keys."""
    return set(filter(false_if_exclamation, key_names))

def get_exclusions(key_names: tuple[str]) -> set[str]:
    """Returns all required unpressed !keys for this macro to trigger."""
    return {key_name[1:] for key_name in key_names if key_name[0] == "!"}

# Runs every time an event is received.
def try_hotkey(currently_held_keys: list[str]):
    """Checks if the current combination of keys is a hotkey, and schedules it to run if so.

    Arguments:
        currently_held_keys: The keys currently held down.
    """
    global _run_these_funcs  # Not necessary, but I prefer explicitly showing it's global.
    global _bound_keys
    global _pressed_keys

    if ctl.DEBUG_SHOW_KEYS:
        print(f"Currently held keys: {currently_held_keys}")

    if _run:  # Don't try to add new macros when the program is idle.
        for key_comb in _bound_keys:

            # Make sure all keys in the combination are pressed.
            if get_inclusions(key_comb) <= currently_held_keys:

                # Make sure no !keys are pressed.
                # (That pressed keys and the "!" exclusions are disjoint.)
                if not get_exclusions(key_comb) & currently_held_keys:

                    # Make sure this only occurs once per key combination.
                    if not _pressed_keys[key_comb]:
                        _run_these_funcs.append(_bound_keys[key_comb])
                        _pressed_keys[key_comb] = True
                else:
                    _pressed_keys[key_comb] = False
            
            else:
                # Update that it's not pressed *after* trying to trigger the functions.
                _pressed_keys[key_comb] = False


# This just exists so the program recognises when keys are unpressed, without having to trigger hotkeys again.
def untry_hotkey(currently_held_keys: list[str]):
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
            if ctl.KEY_WARN:
                print(f"WARNING: {key_str} pressed despite prior pressed status.")
        
        try_hotkey(_currently_held_keys)

    else:
        try:
            _currently_held_keys -= {key_str}
        except ValueError:
            if ctl.KEY_WARN:
                print(f"WARNING: {key_str} released without prior pressed status.")
        
        untry_hotkey(_currently_held_keys)

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
            if ctl.KEY_WARN:
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
            if ctl.KEY_WARN:
                print(f"WARNING: {key_str} released without prior pressed status.")
    
    untry_hotkey(_currently_held_keys)
    # Don't try to check for hotkeys being pressed, otherwise the user would have to focus
    # carefully on which order they release keys from other macros.


def process_macro_string(macro_str: str) -> tuple[str]:
    """Returns a list of strings, each of which is a key combination.

    Arguments:
        macro_string: The string to be split into key combinations.

    Returns:
        A tuple of strings, each string is a SnakeBinds key.
    """
    macro_str = macro_str.replace(" ", "")  # Remove spaces.
    macro_str = macro_str.replace("\n", "")  # Remove newlines.
    macro_str = macro_str.replace("\t", "")  # Remove tabs.
    macro_str = macro_str.replace("\r", "")  # Remove carriage returns.
    macro_str = macro_str.replace("\v", "")  # Remove vertical tabs.

    keyname_list: list[str] = []  # Stores the keys as SnakeBinds strings.

    # If there is no docstring, then it shouldn't try to be a macro.
    if macro_str == "":
        raise ValueError(f"{repr(keyname)} (macro_str) is not a valid pynput identifier or snakebinds alias.")

    macro_keys = macro_str.split("+")

    for keyname in macro_keys:
        # Remove the exclamation mark temporarily while it asseses whether the key is valid.
        if keyname[0] == "!":
            prefix = "!"
            keyname = keyname[1:]
        else:
            prefix = ""

        # Case does not matter for any SnakeBinds macro keys.
        key_lookup = alias_to_snakebind(keyname.lower())  # Convert aliases here.
        if key_lookup is None:
            raise ValueError(f"{repr(keyname)} (macro_str) is not a valid pynput identifier or snakebinds alias.")

        keyname_list.append(prefix + key_lookup)

    keyname_tuple = tuple(keyname_list)  # Use a tuple so it's hashable for a dictionary.
    
    return keyname_tuple


def bind_this_function(new_func: Callable):
    """Takes a function and binds the key combination to running said function.

    Arguments:
        new_func:
            The function to be added to the list of macros.
            It must have a docstring, which is used to create the macro.
    
    Raises:
        NameError: If the key combination is already bound.
        ValueError: If the function has no docstring or the docstring is not a valid macro string.
    """
    macro_str: str = new_func.__doc__

    # If there is no docstring, then it shouldn't try to be a macro.
    if macro_str == "":
        raise ValueError(f"Tried to bind {new_func.__name__} without macro definition.")

    key_comb = process_macro_string(macro_str)

    if key_comb in _bound_keys:
        raise NameError(f"{new_func.__doc__} already defines a macro.")
    _bound_keys[key_comb] = new_func  # new_func will now run when the key combination is pressed.
    _pressed_keys[key_comb] = False  # Initialize the pressed keys to false.


def unbind():
    """Run this to stop checking for macro combinations being pressed."""
    global _run
    global _queued_partials

    if ctl.EMPTY_QUEUE_AFTER_UNBIND:
        _queued_partials = []

    _run = False

def rebind():
    """Run this to start/restart checking for macro combinations being pressed."""
    global _run
    _run = True

    def event_loop():
        global _macro_threads
        while _run:
            # If MACRO_CYCLE_DELAY is 0, this is just a busy wait while _queued_partials or
            # _run_these_funcs are empty.
            time.sleep(ctl.MACRO_CYCLE_DELAY)

            # Every cycle, go through and run all relevant macros requested at that moment in time.
            while _run_these_funcs:
                cur_func = _run_these_funcs.pop(0)  # Take the functions off the list and queue them to run.
                _macro_threads.append(MacroThread(cur_func))
                _macro_threads[-1].start()

                # Joins and makes killable all macro threads that have finished executing.
                map(stop_if_finished, _macro_threads)
                
                _macro_threads = list(filter(is_not_killable, _macro_threads))  # Remove finished threads.
            
            # Similarly, run all queued functions.
            while _queued_partials:
                cur_func = _queued_partials.pop(0)
                cur_func()
    
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

class ctl:
    """Extra functions that help above the simple start/stop (eg bind, unbind, rebind) commands
    available in the module's global namespace."""
    KEY_WARN = False  # Alerts if a key event triggers changing it to a state it's already in.
    DEBUG_SHOW_KEYS = False  # Prints keypress events to the console.
    MACRO_CYCLE_DELAY = 0.002  # How often to test for macro combinations being requested.

    BE_NICE_TO_WINDOWS_PYAUTOGUI = True
    EMPTY_QUEUE_AFTER_UNBIND = True
    THREAD_UNSAFE_OPTIMISATION = False
    # These have the power to give plain pyautogui bindings instead a wrapped version that queues
    # them to run.

    def queue(non_blocking_func: Callable):
        """Queues a function to be run, makes sure this particular function doesn't try to run at
        the same time as other functions in the queue.

        Arguments:
            non_blocking_func:
                Runs a function at the earliest possible opportunity. This function should not have
                significant delays coded into it.
        """
        _queued_partials.append(non_blocking_func)

    def print(*args, **kwargs):
        """Print function that runs in sequence with its time put in the queue with other
        commands."""
        _queued_partials.append(lambda: print(*args, **kwargs))
    
    def import_pyautogui():
        """Use this instead of directly calling pyautogui functions, as this makes sure pyautogui
        calls made in separate threads do not collide - but this is less of a problem on Windows
        systems, you seem to be able to use pyautogui functions in multiple threads with relative
        safety.
        
        It Generates a pyautogui interface that when called, goes through ctl.queue().
        In my opinion, calling pyautogui functions in a crappy macro function is nicer to code
        than using pynput. If someone wants to implement pynput on top of this, be my guest.
        """

        # This just exists so to pretend to have all methods that ever existed in pyautogui.
        class FakePyautogui:
            def __getattr__(self, name: str):
                if hasattr(pyautogui.__dict__[name], "__call__"):
                    def fake_func(*args, **kwargs):
                        ctl.queue(partial(pyautogui.__dict__[name], *args, **kwargs))
                    return fake_func  # When called, it queues the relevant pyautogui function.
                else:
                    return pyautogui.__dict__[name]
            
            def __setattr__(self, name: str, value):
                pyautogui.__dict__[name] = value
        
        if ctl.BE_NICE_TO_WINDOWS_PYAUTOGUI and os == "Windows":
            # Because the above fix is not necessary for Windows, just expose pyautogui straight to
            # the programmer.
            return pyautogui
        elif ctl.THREAD_UNSAFE_OPTIMISATION:
            print("Warning: this can result in uncaught errors in dangling threads causing the \
                program to run silently until reboot. PROCEED WITH CAUTION.")
            return pyautogui
        else:
            return FakePyautogui()
    
    def is_held(macro_str: str) -> bool:
        """Returns True if the macro string is being held down.

        Arguments:
            macro_str:
                A string of keys that are being held down.
        
        Returns:
            True if the macro string is being held down, False otherwise.
        
        Raises:
            ValueError: If the string is not valid.
        """
        key_comb = process_macro_string(macro_str)

        return get_inclusions(key_comb) <= _currently_held_keys and \
                not get_exclusions(key_comb) & _currently_held_keys
        

    def get_pressed_keys() -> list[str]:
        """Returns a list of currently pressed keys.

        Returns:
            A list of currently pressed keys.
        """
        return list(_currently_held_keys)


    # Just so the user doesn't need to track whether it's paused in their scripts.
    def is_running():
        """Shows whether snakebinds is running macros or not."""
        return _run
