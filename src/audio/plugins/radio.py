#if 0 /*
# -----------------------------------------------------------------------
# radio.py - a simple plugin to listen to radio
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
# need to have radio installed before using this plugin
# to activate put the following in your local_conf.py
# plugin.activate('audio.radioplayer')
# plugin.activate('audio.radio')
# RADIO_CMD='/usr/bin/radio'
# RADIO_STATIONS = [ ('Sea FM', '90.9'),
#                    ('Kiss 108', '108'),
#                    ('Mix 98.5', '98.5'),
#                    ('Magic 106', '106.7') ]
# Todo: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/09/22 20:36:17  mikeruelle
# more web interface help descriptions
#
# Revision 1.2  2003/09/20 09:42:32  dischi
# cleanup
#
# Revision 1.1  2003/08/27 15:30:12  mikeruelle
# Start of Radio Support
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

#python modules
import os, popen2, fcntl, select, time

#freevo modules
import config, menu, rc, plugin, skin, util
from audio.player import PlayerGUI
from item import Item


# This is the class that actually runs the commands. Eventually
# hope to add actions for different ways of running commands
# and for displaying stdout and stderr of last command run.
class RadioItem(Item):
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.play , 'Listen to Station' ) ]
        return items

    def play(self, arg=None, menuw=None):
        print self.station+" "+str(self.station_index)+" "+self.name
        # self.parent.current_item = self
        self.elapsed = 0

        if not self.menuw:
            self.menuw = menuw

        self.player = PlayerGUI(self, menuw)
        error = self.player.play()

        if error and menuw:
            AlertBox(text=error).show()
            rc.post_event(rc.PLAY_END)

    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        print 'RadioItem stop'
        self.player.stop()


# this is the item for the main menu and creates the list
# of commands in a submenu.
class RadioMainMenuItem(Item):

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.create_stations_menu , 'stations' ) ]
        return items
 
    def create_stations_menu(self, arg=None, menuw=None):
        station_items = []
        for rstation in config.RADIO_STATIONS:
            radio_item = RadioItem()
            radio_item.name = rstation[0]
            radio_item.station = rstation[1]
            radio_item.type = 'radio'
            radio_item.station_index = config.RADIO_STATIONS.index(rstation)
            radio_item.length = 0
            radio_item.remain = 0
            radio_item.elapsed = 0
            station_items += [ radio_item ]
        if (len(station_items) == 0):
            station_items += [menu.MenuItem('No Stations found', menwu.goto_prev_page, 0)]
        station_menu = menu.Menu('Stations', station_items)
        rc.app(None)
        menuw.pushmenu(station_menu)
        menuw.refresh()

# our plugin wrapper, just creates the main menu item and adds it.
class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin uses the command line program radio to tune a
    bttv card with a radio tuner to a radio station to listen
    to. You need to also use the RadioPlayer plugin to actually
    listen to the station.

    need to have radio installed before using this plugin.
    radio is availble in binary form for most linux distros.

    to activate put the following in your local_conf.py:
    plugin.activate('audio.radioplayer')
    plugin.activate('audio.radio')
    RADIO_CMD='/usr/bin/radio'
    RADIO_STATIONS = [ ('Sea FM', '90.9'),
                       ('Kiss 108', '108'),
                       ('Mix 98.5', '98.5'),
                       ('Magic 106', '106.7') ]

    """
    def items(self, parent):
        menu_items = skin.get_singleton().settings.mainmenu.items

        item = RadioMainMenuItem()
        item.name = 'Radio'
        if menu_items.has_key('radio') and menu_items['radio'].icon:
            item.icon = os.path.join(skin.get_singleton().settings.icon_dir,
                                     menu_items['radio'].icon)
        if menu_items.has_key('radio') and menu_items['radio'].image:
            item.image = menu_items['radio'].image

        item.parent = parent
        return [ item ]


