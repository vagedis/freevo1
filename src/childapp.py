#if 0 /*
# -----------------------------------------------------------------------
# childapp.py - Runs an application in a child process
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.41  2003/11/11 17:59:03  dischi
# remove empty vals from app list
#
# Revision 1.40  2003/11/08 13:18:23  dischi
# support for unicode start strings
#
# Revision 1.39  2003/11/02 12:01:37  dischi
# remove debug
#
# Revision 1.38  2003/11/02 09:24:34  dischi
# Check for libs and make it possible to install runtime from within
# freevo
#
# Revision 1.37  2003/10/27 17:39:35  dischi
# just to be save
#
# Revision 1.36  2003/10/23 17:57:23  dischi
# add kill() function to kill the thread
#
# Revision 1.35  2003/10/22 17:22:36  dischi
# better stop() exception handling
#
# Revision 1.34  2003/10/20 13:46:41  outlyer
# A small change to fix a frequent source of crashes. I don't know why,
# but it happens on occaison, so it's better to silently skip over than
# to crash horribly.
#
# Revision 1.33  2003/10/19 09:51:10  dischi
# better debug
#
# Revision 1.32  2003/10/19 09:07:33  dischi
# support for a list and no string as app to start
#
# Revision 1.31  2003/10/18 17:56:58  dischi
# more childapp fixes
#
# Revision 1.30  2003/10/18 16:51:34  outlyer
# Fix a crash when skipping through tracks.
#
# Revision 1.29  2003/10/18 10:46:37  dischi
# use util popen3 for child control
#
# Revision 1.28  2003/10/14 17:57:32  dischi
# more debug
#
# Revision 1.27  2003/10/11 11:21:14  dischi
# use util killall function
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

import sys
import time
import os
import util.popen3
import threading, thread
import signal
import traceback
import copy

import config
import osd
import rc
import util

from event import *
import rc

__all_childapps__ = []

freevo_shutdown = False

def shutdown():
    """
    shutdown all running childapps
    """
    global __all_childapps__
    global freevo_shutdown
    
    if not len(__all_childapps__):
        return
        
    print '%d child(s) still running, terminate them' % len(__all_childapps__)
    freevo_shutdown = True
    while __all_childapps__:
        print 'shutting down %s' % __all_childapps__[0].binary
        __all_childapps__[0].kill()

        
class ChildApp:

    def __init__(self, app):
        global __all_childapps__
        __all_childapps__.append(self)

        self.lock = thread.allocate_lock()

        if config.DEBUG > 1:
            _debug_('starting new child: %s', app)
            traceback.print_stack()

        prio = 0

        if isinstance(app, unicode):
            app = app.encode(config.LOCALE, 'ignore')
            
        if isinstance(app, str):
            # app is a string to execute. It will be executed by 'sh -c '
            # inside the popen code
            if app.find('--prio=') == 0 and not config.RUNAPP:
                try:
                    prio = int(app[7:app.find(' ')])
                except:
                    pass
                app = app[app.find(' ')+1:]
            if app.find('--prio=') == 0:
                self.binary = app[app.find(' ')+1:].lstrip()
            else:
                self.binary = app.lstrip()
                
            start_str = '%s %s' % (config.RUNAPP, app)


        else:
            # app is a list
            while '' in app:
                app.remove('')

            if app[0].find('--prio=') == 0 and not config.RUNAPP:
                try:
                    prio = int(app[7:app.find(' ')])
                except:
                    pass
                app = copy.copy(app[1:])

            self.binary = str(' ').join(app)

            if config.RUNAPP:
                start_str = [ config.RUNAPP ] + app
            else:
                start_str = app
            
        self.child   = util.popen3.Popen3(start_str)
        self.outfile = self.child.fromchild 
        self.errfile = self.child.childerr
        self.infile  = self.child.tochild
        
        self.t1 = Read_Thread('stdout', self.outfile, self.stdout_cb)
        self.t1.setDaemon(1)
        self.t1.start()
        
        self.t2 = Read_Thread('stderr', self.errfile, self.stderr_cb)
        self.t2.setDaemon(1)
        self.t2.start()

        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))
            
        if config.DEBUG:
            print 'self.t1.isAlive()=%s, self.t2.isAlive()=%s' % (self.t1.isAlive(),
                                                                  self.t2.isAlive())
            time.sleep(0.1)
            if not isinstance(start_str, str):
                start_str = str(' ').join(start_str)
            print 'ChildApp.__init__(), pid=%s, app=%s, poll=%s' % \
                  (self.child.pid, start_str, self.child.poll())
            

    # Write a string to the app. 
    def write(self, line):
        try:
            self.infile.write(line)
            self.infile.flush()
        except (IOError, ValueError):
            pass
        

    # Override this method to receive stdout from the child app
    # The function receives complete lines
    def stdout_cb(self, line):
        pass


    # Override this method to receive stderr from the child app
    # The function receives complete lines
    def stderr_cb(self, line):
        pass


    def isAlive(self):
        return self.t1.isAlive() or self.t2.isAlive()

    
    def kill(self, signal=15):
        global __all_childapps__

        if self in __all_childapps__:
            __all_childapps__.remove(self)
            
        if config.DEBUG > 1:
            _debug_('killing my child')
            traceback.print_stack()

        # killed already
        if hasattr(self,'child'):
            if not self.child:
                _debug_('already dead', 2)
                return
        else:
            _debug_('This should never happen!',1)
            return

        self.lock.acquire()
        # maybe child is dead and only waiting?
        if util.popen3.waitpid(self.child.pid):
            _debug_('done the easy way', 2)
            self.child = None
            if not self.infile.closed:
                self.infile.close()
            self.lock.release()
            return

        if signal:
            _debug_('childapp: killing pid %s signal %s' % (self.child.pid, signal))
            try:
                os.kill(self.child.pid, signal)
            except OSError:
                pass
            
        _debug_('childapp: Before wait(%s)' % self.child.pid)
        for i in range(20):
            if util.popen3.waitpid(self.child.pid):
                break
            time.sleep(0.1)
        else:
            print 'force killing with signal 9'
            try:
                os.kill(self.child.pid, 9)
            except OSError:
                pass
            for i in range(20):
                if util.popen3.waitpid(self.child.pid):
                    break
                time.sleep(0.1)
        _debug_('childapp: After wait()')


        # now check if the app is really dead. If it is, outfile
        # should be closed by the reading thread
        for i in range(5):
            if self.outfile.closed:
                break
            time.sleep(0.1)
        else:
            # Problem: the program had more than one thread, each thread has a
            # pid. We killed only a part of the program. The filehandles are
            # still open, the program still lives. If we try to close the infile
            # now, Freevo will be dead.
            # Solution: there is no good one, let's try killall on the binary. It's
            # ugly but it's the _only_ way to stop this nasty app
            print 'Oops, command refuses to die, try bad hack....'
            util.killall(self.binary, sig=15)
            for i in range(20):
                if self.outfile.closed:
                    break
                time.sleep(0.1)
            else:
                # still not dead. Puh, something is realy broekn here.
                # Try killall -9 as last chance
                print 'Try harder to kill the app....'
                util.killall(self.binary, sig=9)
                for i in range(20):
                    if self.outfile.closed:
                        break
                    time.sleep(0.1)
                else:
                    # Oops...
                    print 'PANIC'
            if not self.infile.closed:
                self.infile.close()
        self.child = None
        self.lock.release()


        
class Read_Thread(threading.Thread):

    def __init__(self, name, fp, callback):
        threading.Thread.__init__(self)
        self.name = name
        self.fp = fp
        self.callback = callback

        
    def run(self):
        try:
            self._handle_input()
        except IOError:
            pass
        except ValueError:
            pass


    def _handle_input(self):
        
        saved = ''
        while 1:

            data = self.fp.readline(300)
            if not data:
                _debug_('%s: No data, stopping (pid %s)!' % (self.name, os.getpid()),2)
                self.fp.close()
                break
            else:
                data = data.replace('\r', '\n')
                lines = data.split('\n')

                # Only one partial line?
                if len(lines) == 1:
                    saved += data
                else:
                    # Combine saved data and first line, send to app
                    self.callback(saved + lines[0])
                    saved = ''

                    # There's one or more lines + possibly a partial line
                    if lines[-1] != '':
                        # The last line is partial, save it for the next time
                        saved = lines[-1]

                        # Send all lines except the last partial line to the app
                        for line in lines[1:-1]:
                            self.callback(line)
                    else:
                        # Send all lines to the app
                        for line in lines[1:]:
                            self.callback(line)
                        


class DummyApp:
    def __init__(self, name=None, parameter=None):
        self.app_name  = name
        self.parameter = parameter
        
    def write(self, string):
        pass

        
class ChildThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mode        = 'idle'
        self.mode_flag   = threading.Event()
        self.stop_osd    = False
        self.app         = DummyApp()
        self.manual_stop = False
        
        self.setDaemon(1)
        threading.Thread.start(self)


    def start(self, app, param):
        """
        set thread to play mode
        """
        self.app         = DummyApp(app, param)
        self.mode        = 'play'
        self.manual_stop = False
        self.mode_flag.set()


    def stop(self, cmd=None):
        if not hasattr(self.app, 'child'):
            for t in traceback.extract_stack():
                if t[0].find('playlist') >= 0:
                    raise OSError

            print 'Tried to stop child when no child is running right now'
            print 'Please send a bug report with the following trace to the'
            print 'Freevo developers'
            traceback.print_stack()
            return

        if config.DEBUG > 1:
            _debug_('got stop command')
            traceback.print_stack()
            
        if cmd and self.app.isAlive():
            self.manual_stop = True
            _debug_('sending exit command to app')
            self.app.write(cmd)
            # wait for the app to terminate itself
            for i in range(20):
                if not self.app.isAlive():
                    break
                time.sleep(0.1)

        self.mode = 'stop'
        self.mode_flag.set()
        while self.mode == 'stop':
            # we are the main thread, we should call the real waitpid()
            util.popen3.waitpid()
            time.sleep(0.1)


    def kill(self):
        try:
            self.stop()
        except OSError:
            pass
        self.mode = 'kill'
        self.mode_flag.set()
        while self.mode != 'killed':
            pass
        

    def run(self):
        global freevo_shutdown
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'kill':
                self.mode = 'killed'
                return
            
            elif self.mode == 'play':

                if self.stop_osd and config.STOP_OSD_WHEN_PLAYING:
                    osd.stop()

                self.app = self.app.app_name(self.app.parameter)
                
                if hasattr(self.app, 'item'):
                    rc.post_event(Event(PLAY_START, arg=self.app.item))
               
                if self.stop_osd:       # Implies a video file
                    rc.post_event(Event(VIDEO_START))

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                # inform Freevo that the app stopped itself
                if self.mode == 'play' and not self.manual_stop:
                    if hasattr(self.app, 'stopped'): 
                        self.app.stopped()
                    else:
                        _debug_('app has no stopped function, send PLAY_END')
                        rc.post_event(PLAY_END)

                if not freevo_shutdown:
                    while self.mode == 'play':
                        _debug_('waiting for main to be ready for the killing', 2)
                        time.sleep(0.1)

                    # kill the app
                    self.app.kill()

                    # Ok, we can use the OSD again.
                    if self.stop_osd and config.STOP_OSD_WHEN_PLAYING:
                        osd.restart()

                    if self.stop_osd:       # Implies a video file
                        rc.post_event(Event(VIDEO_END))

                self.mode = 'idle'

            else:
                self.mode = 'idle'
