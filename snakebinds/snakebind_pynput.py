from __future__ import annotations
"""Converts macro key aliases into snakebind's arbitrary naming system, but it's very similar to pynput's."""

from snakebinds.snakebind_agnostic import snakebind_keys, _alias_lookup_dict


from platform import system as get_os
os = get_os()

# These imports are put here to determine OS based functionality, the idea is that parent modules have no idea of OS.
if os == "Windows":
    from snakebinds.snakebind_pynput_windows import pynput_to_snakebind
elif os == "Linux":
    from snakebinds.snakebind_pynput_linux import pynput_to_snakebind
elif os == "Darwin":
    #from snakebinds.snakebind_pynput_mac import pynput_to_snakebind
    print("MacOS is not supported yet. Using Linux keybinds may work in some cases.")
    from snakebinds.snakebind_pynput_linux import pynput_to_snakebind
else:
    raise NotImplementedError(f"{os} is not supported yet.")

# Tidy these up so it's easier to verify these calls aren't malicious in any way.
del get_os


def is_macro_key(macro_key: str) -> bool:
    """Tells whether the given key is a valid pynput value.

    Args:
        macro_key: The key you are trying to test validity.

    Returns:
        True if it's valid, False if invalid.
    """

    # I have yet to sort out how to allow + or ! as usable macro keys.
    # I would probably say \! and \+ would work fine for future versions to implement.
    # Unfortunately, pressing shift+1 to get ! will not show up as shift+1, it will show as shift+!.

    if macro_key in _alias_lookup_dict.keys() or macro_key in snakebind_keys:
        return True

    elif len(macro_key) == 1:
        return True

    else:
        return False
    # This assumes all single characters are valid, which isn't perfect, but a programmer is much less likely to typo
    # "a" than "ctrl", for example.


def alias_to_snakebind(alias_key: str) -> str | None:
    """Change possible aliases into pynput friendly names.
    
    Args:
        bind_name: A human readable alias.

    Returns:
        A pynput friendly str referring to a key on the keyboard. Returns None if it's not a valid bind_name.
    """

    # There's an assumption here that is_macro_key works. This may not be the case for some single characters.
    if not is_macro_key(alias_key):
        return None

    if alias_key in ("play", "next", "previous"):
        # Specific check where pause/play might be confused with pause/break.
        print("Warning: 'play', 'pause', 'next' and 'previous' are not media keys due to the existence of the \
        pause/break key (named 'pause'), so please use 'media_play', 'media_pause' etc instead.")

    if alias_key in _alias_lookup_dict:  # If alias_key is in alias keys dict, then give it the corresponding snakebind name.
        return _alias_lookup_dict[alias_key]

    else:
        return alias_key  # Else it must be an arbitrary snakebind name already. Assume it's valid.
