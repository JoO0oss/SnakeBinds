# snakebinds
Cross platform macro tool built in Python.

(Please note there is currently a large problem with automating mouse and keyboard inputs, rendering the project pretty much unusable.)

## Use in a project

Currently, I can only recommend copying the folder `snakebinds` into your project to use temporarily, since it is not in a state to more formally publish.


### Example

This just shows briefly a few ways you might construct something with it. One of the things I like about the way it uses docstrings (which I might guess some people will find highly offensive), is that it looks really quite tidy - `example.py` is a version without the comments explaining every keyword.

It exists principly to be a compact way of writing macros in Python.

```python
from snakebinds import bind, unbind
import time
import pyautogui


def test_hotkey():
    """ctrl+shift+t"""
    # Use keyboard names joined with + to create a macro.

    print("Test hotkey runs.")


def alternative_test_hotkey():
    """control+shift+y"""
    # There is a whole host of aliases, just guessing should get you most of the way there.

    print("Alternative test hotkey runs as well.")


def click_hotkey():
    """ctrl+m_forwards"""
    # You can create hotkeys that respond to the mouse as well (this is button 5).

    for _ in range(10):
        pyautogui.click()
        time.sleep(0.05)


def leave_hotkey():
    """ctrl+esc+!shift"""
    # The ! means the hotkey doesn't trigger if you press shift at the same time.

    unbind()
    print("Stopping Macros.")


bind(test_hotkey, alternative_test_hotkey, click_hotkey, leave_hotkey)


```

(I am aware you are supposed to use `if __name__ == "__main__"`, but it would be nothing short of a really bad idea to use something like snakebinds in a big project - where `if __name__ ...` is most useful.)


## Looking forwards
The main reason I'm making something like this is that a super minimal looking AHK-like macro writing project doesn't exist cross-platform. \
So the project intends to be quite minimal, and if it actually functioned (which is a big **IF**), looks fairly similar to what I would imagine it's completed state to be.

To be sure, there can be room to expand, like finding simple way to avoid users making their own calls to [pynput](https://pypi.org/project/pynput/) or [pyautogui](https://pypi.org/project/PyAutoGUI/) for keyboard or mouse inputs, but otherwise it seems mostly there.

The main reason I'm putting it here currently is to expose it to the wider internet to increase the chance of shining a light upon the glaring issues. I have exams coming up, so it's probably going to fall silent for a while. And after those, I will probably create the minimum reproducible example to see if I can work out a fix, or stand a better chance of asking someone more knowledgeable than myself what the root cause is.  

## License
[GPL v2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)