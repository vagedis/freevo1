# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
#
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
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
# -----------------------------------------------------------------------

import os

import osd
import config
import plugin
import dialog


from dialog.display import GraphicsDisplay
from dialog.dialogs import VolumeDialog, MessageDialog

x11_available = False
reason = ''

class PluginInterface(plugin.Plugin):
    """
    Enables the use of a shaped X11 window to display volume/messages and dialogs
    when in external applications like mplayer, xine etc.
    """
    def __init__(self):
        if x11_available:
            self.display = X11GraphicsDisplay()
            dialog.set_overlay_display(self.display)
            plugin.Plugin.__init__(self)
        else:
            self.reason = reason

    def shutdown1(self):
        if x11_available:
            # Nasty hack to kill the connection
            self.display.window = None
            import kaa.display.x11
            del kaa.display.x11._default_x11_display
            kaa.display.x11._default_x11_display = None
            


if config.CONF.display in ('x11', 'xv'):
    try:
        from kaa import imlib2
        from kaa.display import X11Window

        import skins.osd

        class X11GraphicsDisplay(GraphicsDisplay):
            """
            A Display class for showing dialogs on a shaped X11 window.
            """
            def __init__(self):
                super(X11GraphicsDisplay, self).__init__()
                self.window = X11Window(size=(1,1), title='Freevo OSD')
                self.window.set_decorated(False)
                self.window.signals['expose_event'].connect(self.__redraw)
                self.image = None

            def show_volume(self, level, muted, channel=None):
                if self.volume_dialog is None:
                    self.volume_dialog = VolumeDialog()
                    skin = skins.osd.get_definition('overlay_volume')
                    if skin:
                        self.volume_dialog.skin = skin
                super(X11GraphicsDisplay, self).show_volume(level, muted, channel)

            def show_message(self, message):
                dialog = MessageDialog(message)
                skin = skins.osd.get_definition('overlay_message')
                if skin:
                    dialog.skin = skin
                dialog.show()

            def show_image(self, image, position):
                """
                Show the supplied image on the OSD layer.

                @note: Subclasses should override this method to display the image
                using there own mechanism

                @param image: A kaa.imlib2.Image object to be displayed.
                @param position: (x, y) position to display the image.
                """
                self.image = image
                self.window.set_geometry( position, image.size)
                self.window.set_shape_mask_from_imlib2_image(self.image, (0, 0))

                self.window.show()
                self.window.raise_()
                self.window.render_imlib2_image(self.image)


            def hide_image(self):
                """
                Hide the currently displayed image.

                @note: Subclasses should override this method to hide the image
                displayed using show_image()
                """
                self.window.hide()
                self.image = None

            def __redraw(self, regions):
                if self.image:
                    self.window.render_imlib2_image(self.image)

        x11_available = True

    except ImportError:
        reason = 'Failed to find all required modules! Do you have kaa.display installed?'

else:
    reason = 'Not running under X!'
