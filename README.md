# SnakeBinds
Cross platform macro tool built in Python.

As far as I can tell, this is now functional on systems with Python and pynput available.
I have tested it myself on Windows, Ubuntu and Arch (X11, untested on Wayland).

## Use in a project

To be brutally honest, this project (although now functional), is probably best still treated as a _toy project_, so dropping the `snakebinds` folder into the main directory you're coding in is currently the only way to use it. As always, don't blindly trust everything you see on the internet - I've done my best to make it clear any system calls are readable and non-malicious, but it's probably best to avoid running random Python scripts without checking it over or perhaps throwing it into a virtual machine.

The project on Github has the name `SnakeBinds`, it contains a Python module called `snakebinds`, originally the project was also named `snakebinds` with the url lowercase as well, there may be a few mistakes in documentation that hasn't been updated to reflect the more informative capitalisation.


### Example

This just shows, briefly, a few ways you might construct something with it. This stores information in the docstrings (which some people may find highly unpythonic), which makes passing hotkey information with a function tidier - `example.py` is a version without the comments after every keyword.

The project exists principally to write compact Python scripts for keyboard macros.

```python
from snakebinds import bind, unbind, ctl
import time
import pyautogui
# Sneaky tip, depending on your IDE, this gives you all the nice autocompletes etc. without
# affecting your code.

pyautogui = ctl.import_pyautogui()  # Replacement threadsafe pyautogui interface.
pyautogui.PAUSE = 0  # Interacting with constants works identically.


@bind
def test_hotkey():
    """ctrl+shift+t"""
    # Use the decorator @bind, with a docstring of keyboard names joined with + to create a macro.
    
    print("Test hotkey runs.")

@bind
def alternative_test_hotkey():
    """control+shift+y"""
    
    # There is a whole host of hotkey aliases, just guessing should get you most of the way there.
    print("Alternative test hotkey runs as well.")

def click_delay():
    """None-macro function, can be ran by the the programmer as normal."""
    
    # Python functions still all work as normal.
    pyautogui.click()
    time.sleep(0.05)

@bind
def click_hotkey():
    """ctrl+m_forwards"""
    
    # You can create hotkeys that respond to the mouse as well (this is button 5).
    for _ in range(10):
        # click_delay() is a blocking function, but will only hold things up in this function.
        click_delay()

@bind
def hold_click_hotkey():
    """alt+m_forwards"""
    
    # ctl.is_held() can be used to run things while the user holds the macro combination down.
    while ctl.is_held("alt+m_forwards"):
        click_delay()

@bind
def hscroll_right():
    """shift+$r"""

    # Shift + right arrow key
    pyautogui.hscroll(3)  # Scrolls to the right.

@bind
def hscroll_left():
    """shift+$<"""

    # Shift + left arrow key
    pyautogui.hscroll(-3)  # Scrolls to the left.

@bind
def leave_hotkey():
    """ctrl+esc+!shift"""
    # The ! means the hotkey doesn't trigger if you press shift at the same time.
    
    print("Stopping Macros.")
    unbind()  # bind() only stops blocking after this call once all macros have finished.

# The bind() function starts checking for hotkeys being pressed, to stop/finish up, use unbind().
print("Starting Macros.")
bind()
print("Done.")
```

(I am aware it is the convention to use `if __name__ == "__main__"`, but it would be nothing short of a really bad idea to use something like SnakeBinds in a big project - where `if __name__ ...` is most useful.)

There are three functions you can use straight from snakebinds, and then some helper functions from `ctl`, which has constants that can be changed as well.

`bind()` - start listening for hotkey combinations and execute the relevant Python functions. This must be called at least once for the keyboard and mouse listeners to start running. 

`unbind()` - stop listening for hotkey combinations, and by default cancels any queued actions (this behaviour can be changed)

`rebind()` - if you want to start listening for hotkeys again, for whatever reason.

<br>
<br>

`@bind` - this uses the same object as `bind()`, but when used as a decorator adds the function to SnakeBinds' internal list of macros.

`ctl` - 

- `KEY_WARN` (default `False`) Alerts if a key event triggers changing it to a state it's already in.
- `DEBUG_SHOW_KEYS` (default `False`) If true, prints keypress events to the console.
- `MACRO_CYCLE_DELAY` (default `0.002`) How often to test for macro combinations being requested.
- `EMPTY_QUEUE_AFTER_UNBIND` (default `True`) If true, unbind() cancels any queued calls (eg pyautogui).

- `BE_NICE_TO_WINDOWS_PYAUTOGUI` (default `True`) This means Windows users don't queue pyautogui calls, even made from `ctl.import_pyautogui`, since Windows doesn't have the relevant concurrent input problems.
- `THREAD_UNSAFE_OPTIMISATION` (default `False`) Setting this to `True` may speed the program up marginally, you can still queue from `ctl.queue()`.
<br>

- `queue()` - Pass in a function with 0 arguments (or perhaps use partials to fill in the arguements), and it will be queued to run at the earliest opportunity. The functions will execute sequentially in the order they were queued. They all execute in the same thread, one directly after another, so they must be non-blocking functions.
- `print()` - Same as Python's inbuilt `print`, but it is put onto the back of the queue.
- `import_pyautogui()` - In the cases where it ignores the code ensuring thread safety, it just imports `pyautogui` and returns that. Otherwise it takes calls to a fake pyautogui, which queues the function. And when the queued function is executed, that goes to the real pyautogui exactly as if the original call was to pyautogui.
- `is_held()` - Simply pass in the macro string, in the same form as the docstring put on the functions (it doesn't have to have the 3 quotes, of course), and it will just return whether that key combination is held down or not.
- `get_pressed_keys()` - Returns a tuple of strings, each string in the tuple is a key/mouse button, in the SnakeBinds string form. This is useful to see what a key's SnakeBinds string is, because frankly I don't know how each key will turn out. If a string is something weird and unreadable, please submit a bug report, and then maybe that key's pynput identifier coded for specifically.
- `is_running()` - A convenience function, just a bool, True if `bind()` or `rebind()` has been called more recently than `unbind()`.

## Further notes
The main reason I'm making something like this is that minimal looking [AHK](https://www.autohotkey.com)-like macro writing software doesn't seem to exist cross-platform. So the project intends to do as little as it can behind the scenes while allowing less verbose Python scripts to run unrestricted.

To be sure, there can be room to expand, like finding simple way to avoid users making their own calls to [pynput](https://pypi.org/project/pynput/) or [pyautogui](https://pypi.org/project/PyAutoGUI/) for keyboard or mouse inputs, but otherwise it seems mostly there. (`ctl.import_pyautogui()` tries to remedy that, but there is probably a better way, although my main justification was that people don't therefore have to relearn yet another input automation library, and pyautogui is a lot better supported possibly more than SnakeBinds ever will be.)

## License
To be clear, there is no connection to pynput in any way other than it is used in the project. If there is a problem with how SnakeBinds uses pynput, then report that here. Likewise with pyautogui.

Code given here licensed under [GPL v2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).
