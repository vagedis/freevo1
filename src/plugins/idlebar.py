#if 0 /*
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   To activate the idle bar, put the following in your local_config.py
#
#   plugin.activate('idlebar.interface')
#   
#   plugin.activate('idlebar.mail',    level=10, args=('/var/spool/mail/dmeyer', ))
#   plugin.activate('idlebar.tv',      level=20)
#   plugin.activate('idlebar.weather', level=30, args=('4-letter code', ))
#   For weather station codes see: http://www.nws.noaa.gov/tg/siteloc.shtml
#   plugin.activate('idlebar.clock',   level=50)
#   
#
#
# Todo:        
#   Make it cleaner, right now coordinates and fonts are inside the skin
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.20  2003/07/12 17:29:58  dischi
# redraw when polling
#
# Revision 1.19  2003/07/12 17:17:27  dischi
# moved idlebar to a skin plugin
#
# Revision 1.18  2003/07/05 14:57:07  dischi
# the idlebar registers itself as idlebar to the plugin interface
#
# Revision 1.17  2003/07/04 20:14:04  outlyer
# Fixed some confusing logic. It's still confusing, but it works now. Probably
# need to clean this up.
#
# Revision 1.16  2003/07/04 19:48:18  outlyer
# Whoops, fix path.
#
# Revision 1.15  2003/07/04 19:46:51  outlyer
# Added Rich C's "holidays" plugin for the idlebar.
#
# Revision 1.14  2003/07/04 15:17:56  outlyer
# New cdstatus plugin. Only tested on my machine so use with caution.
#
# To use it:
# plugin.activate('idlebar.cdstatus', level=60)
#
# There are a couple of known problems:
#
#     o Only the 'last' drive is shown (last from ROM_DRIVES)
#     o The way that cdbackup tells us we are ripping isn't so nice
#
# Revision 1.13  2003/06/24 22:51:23  outlyer
# Reflect new path to weather icons.
#
# Revision 1.12  2003/06/24 22:48:50  outlyer
# Not sure why this was in /plugins... should be here, in src/plugins
#
# Revision 1.11  2003/06/22 16:53:32  rshortt
# A fix for trying to read the cache when it hasn't been created yet.
#
# Revision 1.10  2003/06/04 23:36:35  rshortt
# Use the real cache dir and add a note about weather codes.
#
# Revision 1.9  2003/05/28 18:12:39  dischi
# pass object to draw to all sub-plugins
#
# Revision 1.8  2003/05/28 17:36:27  dischi
# make the weather zone a parameter
#
# Revision 1.7  2003/05/02 05:50:31  outlyer
# Stopgap to workaround a crash...
#
# Revision 1.6  2003/05/01 12:53:27  dischi
# added more information to plugin draw()
#
# Revision 1.5  2003/04/27 17:59:41  dischi
# use new poll interface
#
# Revision 1.4  2003/04/24 19:56:35  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/19 21:25:00  dischi
# small changes at the plugin interface
#
# Revision 1.2  2003/04/18 10:22:07  dischi
# You can now remove plugins from the list and plugins know the list
# they belong to (can be overwritten). level and args are optional.
#
# Revision 1.1  2003/04/17 21:21:57  dischi
# Moved the idle bar to plugins and changed the plugin interface
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


import time
import os
import config
import sys
import string
import mailbox
import skin

import plugin

import pymetar

TRUE  = 1
FALSE = 0


class interface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 300
        self.plugins = None
        plugin.register(self, 'idlebar')
        self.visible = TRUE
        
    def draw(self, (type, object), osd):
        osd.drawroundbox(0, 0, osd.width, osd.y + 60, (0x80000000, 0, 0, 0))
        if not self.plugins:
            self.plugins = plugin.get('idlebar')
        x = osd.x + 10
        for p in self.plugins:
            add_x = p.draw((type, object), x, osd)
            if add_x:
                x += add_x + 20


    def poll(self):
        skin.get_singleton().redraw()
        

class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type = 'idlebar'
        
    def draw(self, (type, object), x, osd):
        return


class clock(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
    
    def draw(self, (type, object), x, osd):
        clock = time.strftime('%a %I:%M %P')
        font  = osd.get_font('clock')
        osd.write_text(clock, font, None, osd.x + osd.width-200, osd.y + 10, 190,
                       40, 'right', 'center')
        return 0
    

class cdstatus(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.cdimages ={}
        self.cdimages ['audio'] = 'skins/images/status/cd_audio.png'
        self.cdimages ['empty_cdrom'] = 'skins/images/status/cd_inactive.png'
        self.cdimages ['images'] = 'skins/images/status/cd_photo.png'
        self.cdimages ['video'] = 'skins/images/status/cd_video.png'
        self.cdimages ['burn'] ='skins/images/status/cd_burn.png'
        self.cdimages ['cdrip'] = 'skins/images/status/cd_rip.png'
        self.cdimages ['mixed'] = 'skins/images/status/cd_mixed.png'

    def draw(self, (type, object), x, osd):
        image = self.cdimages['empty_cdrom']
        for media in config.REMOVABLE_MEDIA:
            if hasattr(media.info,'type') and hasattr(media.info,'handle_type'):
                if not media.info.handle_type and media.info.type:
                    image = self.cdimages['mixed']
                elif media.info.handle_type: 
                    image = self.cdimages[media.info.handle_type]
        return osd.draw_image(image, (x, osd.y + 15, -1, -1))[0]


class mail(IdleBarPlugin):
    def __init__(self, mailbox):
        IdleBarPlugin.__init__(self)
        self.NO_MAILIMAGE = 'skins/images/status/newmail_dimmed.png'
        self.MAILIMAGE = 'skins/images/status/newmail_active.png'
        self.MAILBOX = mailbox

    def checkmail(self):
        if not self.MAILBOX:
            return 0
        if os.path.isfile(self.MAILBOX):
            mb = mailbox.UnixMailbox (file(self.MAILBOX,'r'))
            msg = mb.next()
            count = 0
            while msg is not None:
                count = count + 1
                msg = mb.next()
            return count
        else:
            return 0

    def draw(self, (type, object), x, osd):
        if self.checkmail() > 0:
            return osd.draw_image(self.MAILIMAGE, (x, osd.y + 10, -1, -1))[0]
        else:
            return osd.draw_image(self.NO_MAILIMAGE, (x, osd.y + 10, -1, -1))[0] 




class tv(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.tvlockfile = config.FREEVO_CACHEDIR + '/record'
        self.TVLOCKED = 'skins/images/status/television_active.png'
        self.TVFREE = 'skins/images/status/television_inactive.png'
        
    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0

    def draw(self, (type, object), x, osd):
        if self.checktv() == 1:
            return osd.draw_image(self.TVLOCKED, (x, osd.y + 10, -1, -1))[0]
        else:
            return osd.draw_image(self.TVFREE, (x, osd.y + 10, -1, -1))[0]



class weather(IdleBarPlugin):
    def __init__(self, zone='CYYZ'):
        IdleBarPlugin.__init__(self)
        self.METARCODE = zone
        self.WEATHERCACHE = config.FREEVO_CACHEDIR + '/weather'
        self.CLOCKFONT = 'skins/fonts/Trebuchet_MS.ttf'
        if not os.path.isfile(self.CLOCKFONT):
            # XXX Get this from the skin, but for now this will allow it to work
            self.CLOCKFONT = config.OSD_DEFAULT_FONTNAME

    def checkweather(self):
        # We don't want to do this every 30 seconds, so we need
        # to cache the date somewhere. 
        # 
        # First check the age of the cache.
        #
        if (os.path.isfile(self.WEATHERCACHE) == 0 or \
            (abs(time.time() - os.path.getmtime(self.WEATHERCACHE)) > 3600)):
            weather = pymetar.MetarReport()
            try:
                weather.fetchMetarReport(self.METARCODE)
                if (weather.getTemperatureCelsius()):
                    temperature = '%2d' % weather.getTemperatureCelsius()
                else:
                    temperature = '0'  # Make it a string to match above.
                if weather.getPixmap():
                    icon = weather.getPixmap() + '.png'
                else:
                    icon = 'sun.png'
                cachefile = open(self.WEATHERCACHE,'w+')
                cachefile.write(temperature + '\n')
                cachefile.write(icon + '\n')
                cachefile.close()
            except:
                # HTTP Problems, use cache. Wait till next try.
                try:
                    cachefile = open(self.WEATHERCACHE,'r')
                    newlist = map(string.rstrip, cachefile.readlines())
                    temperature,icon = newlist
                    cachefile.close()
                except IOError:
                    print 'WEATHER: error reading cache. Using fake weather.'
                    return '0', 'sun.png'

        else:
            cachefile = open(self.WEATHERCACHE,'r')
            newlist = map(string.rstrip, cachefile.readlines())
            temperature,icon = newlist
            cachefile.close()
        return temperature, icon

    def draw(self, (type, object), x, osd):
        temp,icon = self.checkweather()
        font  = osd.get_font('weather')
        osd.draw_image('skins/icons/weather/' + icon, (x, osd.y + 15, -1, -1))
        temp = '%s�' % temp
        width = font.font.stringsize(temp)
        osd.write_text(temp, font, None, x + 15, osd.y + 55 - font.h, width, font.h,
                       'left', 'top')
        return width + 15
        
# This class checks if the current date is a holiday and will
# display a user specified icon for that holiday.    
# To activate use the following: 
# plugin.activate('idlebar.holidays', level=40)        
# I am centering Icon over the clock, w x h = 70 x 40 pixels works well,
# with drawbitmap drawing at x,y= 580, 2
class holidays(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
   
    def get_holiday_icon(self):
        if not config.HOLIDAYS:
            return 0    
        else:
           # Creates a string which looks like "07-04" meaning July 04
            todays_date = time.strftime('%m-%d')
            
            for i in config.HOLIDAYS:                        
                holiday, icon = i
                if todays_date == holiday:
                    return icon

    def draw(self, (type, object), x, osd):
        icon = self.get_holiday_icon()
        if icon:
            return osd.draw_image('skins/images/holidays/' + icon, (x, osd.y + 10, -1, -1))[0]
