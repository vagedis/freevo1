#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.11  2003/08/17 17:16:44  dischi
# cache less for urls to save time
#
# Revision 1.10  2003/06/29 02:36:01  rshortt
# Now works with mplayer's new audio (string) format.  The way I did this
# seems a bit repetitive so feel free to make it better.
#
# Revision 1.9  2003/06/06 14:13:00  outlyer
# Patch for audiofiles with length > 1000sec from Urmet... I made a similar
# fix for video awhile back, don't know why I forgot audio.
#
# Revision 1.8  2003/05/28 15:34:43  dischi
# fixed seeking bug
#
# Revision 1.7  2003/05/28 15:02:49  dischi
# ported detach plugin to new event model and other small fixes
#
# Revision 1.6  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.5  2003/05/08 14:17:38  outlyer
# Initial version of Paul's FXD radio station support. I made some changes from
# the original patch, in that I added an URL field to the audioitem class instead of
# using the year field as his patch did. I will be adding a example FXD file to
# testfiles as well.
#
# Revision 1.4  2003/04/24 19:56:07  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/22 11:57:07  dischi
# added STOP
#
# Revision 1.2  2003/04/21 18:40:33  dischi
# use plugin name structure to find the real player
#
# Revision 1.1  2003/04/21 13:26:12  dischi
# mplayer is now a plugin
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

import time, os
import string
import threading, signal
import re

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications

import rc
import plugin
from event import *


DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# contains an initialized MPlayer() object
mplayer = None


class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the audio player. Use mplayer to play all audio
    files.
    """
    def __init__(self):
        global mplayer
        # create the mplayer object
        plugin.Plugin.__init__(self)
        mplayer = util.SynchronizedObject(MPlayer())

        # register it as the object to play audio
        plugin.register(mplayer, plugin.AUDIO_PLAYER)


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
        self.app_mode = 'audio'

        
    def get_demuxer(self, filename):
        DEMUXER_MP3 = 17
        DEMUXER_OGG = 18
        rest, extension     = os.path.splitext(filename)
        if string.lower(extension) == '.mp3':
            return "-demuxer " + str(DEMUXER_MP3)
        if string.lower(extension) == '.ogg':
            return "-demuxer " + str(DEMUXER_OGG)
        else:
            return ''


    def play(self, item, playerGUI):
        """
        play a audioitem with mplayer
        """
        if item.url:
            filename = item.url
        else:
            filename = item.filename

        self.playerGUI = playerGUI
        
        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0

        if not os.path.isfile(filename) and not network_play:
            return '%s\nnot found!' % os.path.basename(filename)
            
        # Build the MPlayer command
        mpl = '--prio=%s %s -slave %s' % (config.MPLAYER_NICE,
                                          config.MPLAYER_CMD,
                                          config.MPLAYER_ARGS_DEF)

        if not network_play:
            demux = ' %s ' % self.get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

        extra_opts = item.mplayer_options
        command = '%s -vo null -ao %s %s %s "%s"' % (mpl, config.MPLAYER_AO_DEV,
                                                     demux, extra_opts, filename)

        if network_play:
            command = '%s -cache 100' % command
            
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item
        self.thread.item = item

        if not self.thread.item.valid:
            # Invalid file, show an error and survive.
            return 'Invalid audio file'

        self.thread.play_mode = self.mode

        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        self.thread.item = None
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def is_playing(self):
        return self.thread.mode != 'idle'

    def refresh(self):
        self.playerGUI.refresh()
        
    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if event == AUDIO_PLAY_END:
            event = PLAY_END
            
        if event == AUDIO_SEND_MPLAYER_CMD:
            self.thread.app.write('%s\n' % event.arg)
            return TRUE

        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        elif event == PAUSE or event == PLAY:
            self.thread.app.write('pause\n')
            return TRUE

        elif event == SEEK:
            self.thread.app.write('seek %s\n' % event.arg)
            return TRUE

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
            
            
# ======================================================================

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, app, item):
        if config.MPLAYER_DEBUG:
            startdir = os.environ['FREEVO_STARTDIR']
            fname_out = os.path.join(startdir, 'mplayer_stdout.log')
            fname_err = os.path.join(startdir, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'a')
                self.log_stderr = open(fname_err, 'a')
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'MPlayer logging!') % (fname_out, fname_err))
                print 'Please set MPLAYER_DEBUG=0 in local_conf.py, or '
                print 'start Freevo from a directory that is writeable!'
                print
            else:
                print 'MPlayer logging to "%s" and "%s"' % (fname_out, fname_err)

        self.item = item
        self.elapsed = 0
        childapp.ChildApp.__init__(self, app)
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
	self.RE_TIME_NEW = re.compile("^A: *([0-9]+):([0-9]+)").match
              
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)
        if config.MPLAYER_DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()

    def stdout_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stdout.write(line + '\n')
            except ValueError:
                pass # File closed
                     
        if line.startswith("A:"):         # get current time
            m = self.RE_TIME_NEW(line)
            if m:
		timestrs = string.split(m.group(),":")
		if len(timestrs) == 5:
		    # playing for days!
                    self.item.elapsed = 86400*int(timestrs[1]) + \
		                        3600*int(timestrs[2]) + \
		                        60*int(timestrs[3]) + \
					int(timestrs[4])
                elif len(timestrs) == 4:
		    # playing for hours
                    self.item.elapsed = 3600*int(timestrs[1]) + \
		                        60*int(timestrs[2]) + \
					int(timestrs[3])
                elif len(timestrs) == 3:
		    # playing for minutes
                    self.item.elapsed = 60*int(timestrs[1]) + int(timestrs[2])
                elif len(timestrs) == 2:
		    # playing for only seconds
                    self.item.elapsed = int(timestrs[1])
            else:
                m = self.RE_TIME(line) # Convert decimal 
                if m:
                    self.item.elapsed = int(m.group(1))

            if self.item.elapsed != self.elapsed:
                mplayer.refresh()
            self.elapsed = self.item.elapsed



    def stderr_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stderr.write(line + '\n')
            except ValueError:
                pass # File closed
                     

# ======================================================================

class MPlayer_Thread(threading.Thread):
    """
    Thread to wait for a mplayer command to play
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.play_mode = ''
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.item      = None

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    rc.post_event(AUDIO_PLAY_END)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'
