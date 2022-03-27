# SnakeBinds
Cross platform macro tool built in Python.

I can confirm it works on Windows 10, but there may be issues on Linux with GTK doing things the way I thought it does things - and also there maybe issues with different distros.

## Use in a project

To be brutally honest, this project (although now vaguely functional), is probably best still treated as a _toy project_, so dropping the `snakebinds` folder into the main directory you're coding in is currently the only way to use it. As always, don't blindly trust everything you see on the internet - I've done my best to make it clear any system calls are readable and non-malicious, but it's probably best to avoid running random Python scripts without checking it over or perhaps throwing it into a virtual machine.

The project on Github has the name `SnakeBinds`, it contains a Python module called `snakebinds`, originally the project was also named `snakebinds` with the url lowercase as well, there may be a few mistakes in documentation that hasn't been updated to reflect the informative capitalisation.


### Example

This just shows, briefly, a few ways you might construct something with it. This stores information in the docstrings (which some people may find highly unpythonic), which makes passing hotkey information with a function tidier - `example.py` is a version without the comments after every keyword.

The project exists principally to write compact Python scripts for keyboard macros.

```python
from snakebinds import bind, unbind
import time
import pyautogui

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
        click_delay()

@bind
def leave_hotkey():
    """ctrl+esc+!shift"""
    # The ! means the hotkey doesn't trigger if you press shift at the same time.
    
    print("Stopping Macros.")
    unbind()

# The bind() function starts checking for hotkeys being pressed, to stop/finish up, use unbind().
bind()
```

(I am aware it is the convention to use `if __name__ == "__main__"`, but it would be nothing short of a really bad idea to use something like SnakeBinds in a big project - where `if __name__ ...` is most useful.)

There are two other functions:

`rebind()` - if you want to start listening for hotkeys again, for whatever reason.

`is_running()` - to tell whether listening for hotkeys has been paused without verbose flags every time you `unbind()`/`rebind()`.


## Further notes
The main reason I'm making something like this is that minimal looking [AHK](https://www.autohotkey.com)-like macro writing software doesn't seem to exist cross-platform. So the project intends to do as little as it can behind the scenes while allowing less verbose Python scripts to run unrestricted.

To be sure, there can be room to expand, like finding simple way to avoid users making their own calls to [pynput](https://pypi.org/project/pynput/) or [pyautogui](https://pypi.org/project/PyAutoGUI/) for keyboard or mouse inputs, but otherwise it seems mostly there.

## License
To be clear, there is no connection to pynput in any way other than it is used in the project. If there is a problem with how SnakeBinds uses pynput, then report that here.

Code given here licensed under [GPL v2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).
