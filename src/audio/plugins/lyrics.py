# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# lyrics - show the lyrics from a song
# -----------------------------------------------------------------------
#
# Notes:
# Todo: parse the special characters in the lyrics
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
# -----------------------------------------------------------------------

import time, os, re
import plugin, menu, rc

import urllib, urllib2

from gui.PopupBox import PopupBox
from event import *
from skin.widgets import ScrollableTextScreen

LEOLYRICS_AUTH = "Freevo"

class PluginInterface(plugin.ItemPlugin):
    """
    Displays the lyric of a selected song.

    The lyrics are fetched from http://leoslyrics.com.

    To activate this plugin use:
    | plugin.activate('audio.lyrics')
    """

    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def search_lyrics(self, arg=None, menuw=None):
        box = PopupBox(text=_('Searching lyrics...'))
        box.show()
        lyrics = self.fetch_lyric_leoslyrics()

        if lyrics != False:
            box.destroy()
            ShowDetails(menuw, self.item, lyrics)
        else:
            box.destroy()
            box = PopupBox(text=_('Lyrics not found, sorry...'))
            box.show()
            time.sleep(3)
            box.destroy()
        return

    def actions(self, item):
        self.item = item

        if item.type == 'audio':
            return [ (self.search_lyrics, _("Show lyrics"), self) ]

        return []

    def fetch_lyric_leoslyrics(self):
        result_code = -1
        try:
            url = "http://api.leoslyrics.com/api_search.php?auth=%s&artist=%s&songtitle=%s"%(
                LEOLYRICS_AUTH,
                urllib.quote(self.item.info['artist'].encode('utf-8')),
                urllib.quote(self.item.info['title'].encode('utf-8')))
            info = urllib2.urlopen(url).read()
            result_code = re.search('.+<response code="(\d)">.+',info).group(1)
        except:
            print "Error searching for artist/title."
            return False

        if result_code == '0': #ok
            #get the hid
            filter_info = re.search('.+hid="(.+)" exactMatch="true".+', info)
            if filter_info:
                hid = '"' + filter_info.group(1) + '"'

            #fetch the new url
            try:
                url2 =  "http://api.leoslyrics.com/api_lyrics.php?auth=%s&hid=%s"%(
                        LEOLYRICS_AUTH,
                        urllib.quote(hid.encode('utf-8')))
                lyrics_raw = urllib2.urlopen(url2).read()
                reg_expr = re.compile('.+<text>(.+)</text>.+', re.DOTALL|re.MULTILINE)
                self.lyrics = re.search(reg_expr, lyrics_raw).group(1)
                self.lyrics = self.lyrics.replace("&#xD;", os.linesep)
                self.lyrics = self.lyrics.replace('\r\n','')
                self.lyrics = self.lyrics.replace('&amp;','&')
                return Unicode(self.lyrics, encoding='utf-8')
            except:
                print "Error fetching lyrics."
                return False
        else:
            return False

########################
# Show Text

import skin
# Create the skin_object object
skin_object = skin.get_singleton()
if skin_object:
    skin_object.register('tvguideinfo', ('screen', 'info', 'scrollabletext', 'plugin'))

# Program Info screen
class ShowDetails(ScrollableTextScreen):
    """
    Screen to show more details
    """
    def __init__(self, menuw, audio, lyrics):
        ScrollableTextScreen.__init__(self, 'tvguideinfo', lyrics)
        self.name = audio.name
        self.audio           = audio
        self.show(menuw)


    def getattr(self, name):
        if name == 'title':
            return self.name

        if self.audio:
            return self.audio.getattr(name)

        return u''


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for the programm description display
        """
        event_consumed = ScrollableTextScreen.eventhandler(self, event, menuw)

        if not event_consumed:
            if event == MENU_PLAY_ITEM:
                self.menuw.delete_menu()
                self.menuw.delete_submenu(refresh = False)
                # try to watch this program
                self.audio.play(menuw=self.menuw)
                event_consumed = True

        return event_consumed
