from pynput import mouse, keyboard

def pynput_to_snakebind(key: keyboard.Key | keyboard.KeyCode | mouse.Button) -> str:
    """Take a pynput key and return the equivalent snakebind key."""
    pynput_key: str = ""
    
    if isinstance(key, mouse.Button):
        if key.name == "x1":
            pynput_key = "mouse_backward"
        elif key.name == "x2":
            pynput_key = "mouse_forward"
        else:
            pynput_key = "mouse_" + key.name

    elif hasattr(key, "name"):
        pynput_key = key.name
    else:
        pynput_key = str(key).lower().replace("'", "")

    if pynput_key == "ctrl_l":
        pynput_key = "ctrl"
    
    if pynput_key[:2] == r"\x":
        return chr(int(pynput_key[2:], 16) + 96)

    return pynput_key

def convert_key(key: keyboard.Key | keyboard.KeyCode | mouse.Button) -> str:
    """Converts a pynput key object to a string."""
    converted: str = ""
    
    if isinstance(key, mouse.Button):
        converted = "mouse_" + key.name

    elif hasattr(key, "name"):
        converted = key.name
    else:
        converted = str(key).lower().replace("'", "")

    if converted == "ctrl_l":
        converted = "ctrl"

    return converted
