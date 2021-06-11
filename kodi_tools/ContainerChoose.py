from mycroft.util.log import LOG
import requests
import json
from math import ceil
#from mycroft.util.log import LOG


# Based on pause_player
def info_labels(kodi_path, labels):
    """
    Get specified info labels.
    """
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "XBMC.GetInfoLabels"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "labels": labels
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return(json.loads(kodi_response.text)['result'])
    except Exception as e:
        LOG.info(e)

def get_widelist_screen_options(kodi_path):
    """Get one screen of options, for a viewmode such as Widelist"""
    # assumes that Container().Viewmode is WideList
    # WARNING: DIRTY HACK.  Replace if the JSONRPC gives us better options later.
    # get the cursor position, the number of items, and the number of pages
    data = info_labels(kodi_path, ['Container().NumPages', 'Container().NumAllItems', 'Container().Position',
                                   'Container().CurrentItem'])
    num_items = int(data['Container().NumAllItems'])
    num_pages = int(data['Container().NumPages'])
    cur_pos_on_screen = int(data['Container().Position'])
    #cur_pos_in_list = int(data['Container().CurrentItem'])

    # use the number of pages and number of items to get an upper bound on the number of items per page
    #DIRTY HACK: I couldn't find the number of items per page, so guess high if there's one page.
    # We need to do this because the top position might be higher than 1.
    if num_pages == 1:
        bound_pagelen = 30
    else:
        bound_pagelen = num_items//(num_pages - 1)
    # get the labels for each item
    vis_positions = range(bound_pagelen)
    itemlabel_queries = ["Container().ListItemPosition(" + str(i) + ").Label" for i in vis_positions]
    labeldata = info_labels(kodi_path, itemlabel_queries)
    # filter the positions and labels and generate offsets
    # return (hoffset, voffset, label) tuples in a list
    return([(0, i - cur_pos_on_screen,labeldata[q])
            for i, q in zip(vis_positions, itemlabel_queries)
            if len(labeldata[q]) > 0])

def get_horizontal_options(kodi_path):
    """Gets all options in a horizontal Container ViewMode such as Shift."""
    # For Container().Viewmode Shift. Get everything instead of just on-scren because of the low information density.
    # get the cursor position and the number of items.
    data = info_labels(kodi_path, ['Container().NumAllItems', 'Container().CurrentItem'])
    num_items = int(data['Container().NumAllItems'])
    cur_idx = int(data['Container().CurrentItem'])
    # get the labels for each item
    itemlabel_queries = ["Container().ListItemAbsolute(" + str(i) + ").Label" for i in range(num_items)]
    labeldata = info_labels(kodi_path, itemlabel_queries)
    # return (hoffset, voffset, label) tuples in a list
    return([(i - cur_idx, 0, labeldata[q])
            for i, q in zip(range(num_items), itemlabel_queries)
            if len(labeldata[q]) > 0])

import requests
import json
from .MoveCursor import move_cursor_batch

def select_list_item_by_tuple(kodi_path, item_tuple):
    """Select an item from the current Container with movement inputs.
    Input: kodi_path and (x_offset, y_offset, label) tuple."""
    (x, y, _) = item_tuple
    # Move left or up before right or down in case we're in the last row of a grid
    # (Not currently implemented)
    batch = []
    if x < 0:
        batch.extend(["Left"]* -x)
    if y < 0:
        batch.extend(["Up"] * -y)
    if x > 0:
        batch.extend(["Right"]* x)
    if y > 0:
        batch.extend(["Down"]* y)
    batch.append("Select")
    move_cursor_batch(kodi_path, batch)
