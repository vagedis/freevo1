#if 0 /*
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/09/21 13:15:56  dischi
# handle audio fxd files correctly
#
# Revision 1.6  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif

import config
import util

from audioitem import AudioItem


def cwd(parent, files):
    """
    return a list of items based on the files
    """
    items = []

    for file in util.find_matches(files, config.SUFFIX_AUDIO_FILES + [ 'fxd' ]):
        a = AudioItem(file, parent)
        if a.valid:
            items.append(a)
            files.remove(file)

    return items



def update(parent, new_files, del_files, new_items, del_items, current_items):
    """
    update a directory. Add items to del_items if they had to be removed based on
    del_files or add them to new_items based on new_files
    """
    for item in current_items:
        for file in util.find_matches(del_files, config.SUFFIX_AUDIO_FILES):
            if item.type == 'audio' and item.filename == file:
                del_items += [ item ]
                del_files.remove(file)

    new_items += cwd(parent, new_files)
