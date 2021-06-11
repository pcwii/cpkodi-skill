import requests
import json
from .MoveCursor import move_cursor

def select_list_item_by_tuple(kodi_path, item_tuple):
    """Select an item from the current Container with movement inputs.
    Input: kodi_path and (x_offset, y_offset, label) tuple."""
    (x, y, _) = item_tuple
    # Move left or up before right or down in case we're in the last row of a grid
    # (Not currently implemented)
    if x < 0:
        for _ in range(-x):
            move_cursor(kodi_path, "Left")
    if y < 0:
        for _ in range(-y):
            move_cursor(kodi_path, "Up")
    if x > 0:
        for _ in range(x):
            move_cursor(kodi_path, "Right")
    if y > 0:
        for _ in range(y):
            move_cursor(kodi_path, "Down")
    move_cursor(kodi_path, "Select")

def jumpsms_select(kodi_path, item_label):
    """Selects an item by name with the jumpsms system,
    which lets you select something by typing it on an SMS keyboard.
    Awful hack."""
    # find a sequence of commands that searches this item
    commands = [letter_to_number(c) for c in item_label.lower()
                if c in 'abcdefghipqrstuvwxyz']
    # bake it into a batch of rpc calls
    # make sure that we now have the right item focused before we click it

def letter_to_number(char):
    if char in 'abc':
        return 'jumpsms2'
    if char in 'def':
        return 'jumpsms3'
    if char in 'ghi':
        return 'jumpsms4'
    if char in 'jkl':
        return 'jumpsms5'
    if char in 'mno':
        return 'jumpsms6'
    if char in 'pqrs':
        return 'jumpsms7'
    if char in 'tuv':
        return 'jumpsms8'
    if char in 'wxyz':
        return 'jumpsms9'
    return None

