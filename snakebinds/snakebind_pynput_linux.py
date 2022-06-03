from __future__ import annotations
from pynput import mouse, keyboard

def pynput_to_snakebind(key: keyboard.Key | keyboard.KeyCode | mouse.Button) -> str:
    """Take a pynput key and return the equivalent snakebind key."""
    pynput_key: str = ""
    
    if isinstance(key, mouse.Button):
        if key.name == "button8":
            pynput_key = "mouse_backward"
        elif key.name == "button9":
            pynput_key = "mouse_forward"
        else:
            pynput_key = "mouse_" + key.name

    elif hasattr(key, "name"):
        pynput_key = key.name
    else:
        pynput_key = str(key).lower().replace("'", "")

    if pynput_key == "ctrl_l":
        pynput_key = "ctrl"
    
    return pynput_key
