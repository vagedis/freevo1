# ----------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module. 
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/10/31 21:11:02  dischi
# playlist parser, returns a list of all files. There a separat functions
# for the different types of playlists. Feel free to add more
#
#
# ----------------------------------------------------------------------
#
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
# ----------------------------------------------------------------------


import sys
import random
import time, os
import string
import popen2
import fcntl
import select
import struct


def read_m3u(plsname):
    """
    This is the (m3u) playlist reading function.

    Arguments: plsname  - the playlist filename
    Returns:   The list of interesting lines in the playlist
    """
    
    try:
        lines = open(plsname).readlines()
    except IOError:
        print 'Cannot open file "%s"' % list
        return 0
    
    playlist_lines_dos = map(lambda l: l.strip(), lines)
    playlist_lines     = filter(lambda l: l[0] != '#', playlist_lines_dos)

    return playlist_lines

def read_pls(plsname):
    """
    This is the (pls) playlist reading function.

    Arguments: plsname  - the playlist filename
    Returns:   The list of interesting lines in the playlist
    """
    
    try:
        lines = open(plsname).readlines()
    except IOError:
        print 'Cannot open file "%s"' % list
        return 0
    
    playlist_lines_dos = map(lambda l: l.strip(), lines)
    playlist_lines = filter(lambda l: l[0:4] == 'File', playlist_lines_dos)

    for line in playlist_lines:
        numchars=line.find("=")+1
        if numchars > 0:
                playlist_lines[playlist_lines.index(line)] = \
                                                line[numchars:]

    return playlist_lines


def read_playlist(playlist_file, start_playing=0):
    """
    This is the (m3u/pls) playlist handling function.

    Arguments: arg[0]  - the playlist filename
    Returns:   Boolean
    """
    (curdir, playlistname) = os.path.split(playlist_file)

    f=open(playlist_file, "r")
    line = f.readline()
    f.close
    if line.find("[playlist]") > -1:
        playlist_lines = read_pls(playlist_file)
    else:
        playlist_lines = read_m3u(playlist_file)
                
    if start_playing and len(playlist_lines):
        play(arg=('audio', playlist_lines[0], playlist_lines))
        return 0

    items = []
    for line in playlist_lines:
        if line.rfind("://") == -1:
                # it seems a file
                (dirname, filename) = os.path.split(line)

                # that doesn't have a path or is absolute
                if not dirname: 
                        dirname = curdir

                playlist_lines[playlist_lines.index(line)] = \
                              os.path.join(os.path.abspath(dirname), filename) 
        

    return playlist_lines
