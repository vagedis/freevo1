#if 0 /*
# -----------------------------------------------------------------------
# df.py - really simple diskfree plugin for freevo
# created by den_RDC
# -----------------------------------------------------------------------
# $Id$
#
# Notes: but plugin.activate('df') in your local_conf.py. You can see the
#        disc usage by pressing ENTER on a directory item
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.6  2003/09/09 18:55:00  dischi
# Add some doc
#
# Revision 1.5  2003/08/23 12:51:42  dischi
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


import plugin
import util

class PluginInterface(plugin.ItemPlugin):
    """
    This plugin adds an item to your Audio, Video, Games, and Pictures Items. It
    states how much memory is free on the partition that directory belongs to.

    to activate it, put this in your local_conf.py:

    plugin.activate('df') 

    to see the disk usage go to any directory listing and, press ENTER ('e' key or
    key it maps to on your remote) and you will see the disk usage under the Browse
    directory option. This also works on the main directory listings where you see
    your cdrom drives.
    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def actions(self, item): 
        if item.type == 'dir':
            diskfree = _('%i of %i Mb free')  % \
                       ( (( util.freespace(item.dir) / 1024) / 1024),
                         ((util.totalspace(item.dir) /1024) /1024))
            return  [ ( self.dud, diskfree) ]
        else:
            return []


    def dud(self, arg=None, menuw=None):
        pass
