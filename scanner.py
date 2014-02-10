#!/usr/bin/env python
import sys, os, time
import pygtk, gtk
import zbarpygtk

import ticket_security
from user_database import User

SIZE = (800, 600)
GOOD = True
BAD  = False
NEITHER = None
good_message_color    = gtk.gdk.color_parse("#ACF7A8")
bad_message_color     = gtk.gdk.color_parse("#F7A8A8")
neither_message_color = gtk.gdk.color_parse("#D3D3D3")

signer = ticket_security.TicketSigner()


class TicketScanner(object):

    def _check_user(self, username, id_confirm):
        """Checks user details, moving into the wristbanding state on success"""
        try:
            # A base assumption of this system is that the ticket signer is
            # trustworthy. Thus, the user validity isn't checked, only that
            # they're not checked in already.

            is_checked_in = User.is_checked_in(username)
            if is_checked_in:
                self._error_state("User '{}' already checked-in".format(username))
            else:
                if id_confirm:
                    self._set_message("Waiting for identity confirmation...", GOOD)
                    self._can_scan = False
                    if not self._confirm_identity_dialog():
                        self._ready_state()
                        return

            self._wristband_state("\nUser '{}' ({}) can be wristbanded".format(user.fullname,
                                                                                 username))

        except ValueError as e:
            self._error_state(str(e))


    def _decoded(self, zbar, data):
        """Callback from zbar when a QR code is detected"""

        if not self._can_scan:
            self._log("Can't scan, waiting for current user to be processed")
            return

        if not data.startswith("QR-Code:"):
            raise ValueError("Received something other than a QR Code")
        data = data[len("QR-Code:"):]

        try:
            username = signer.verify(data)
            self._check_user(username, False)
            self.current_username = username

        except ValueError as e:
            self._error_state(str(e))


    def _wristband_click(self, widget, data=None):
        User.mark_checked_in(self.current_username)
        self._log(self.current_username, "has been wristbanded")
        self._ready_state()

    def _abort_click(self, widget, data=None):
        self._ready_state()


    def _manual_click(self, widget, data=None):
        if not self._can_scan:
            self._log("Can't manually check, waiting for current user to be processed")
            return

        try:
            username = self._manual_entry.get_text()
            if len(username) == 0:
                return
            self._check_user(username, True)

        except ValueError as e:
            self._error_state(str(e))


    def _confirm_identity_dialog(self):
        """Creates a yes/no dialog returning True when the user's identity is confirmed"""
        dialog = gtk.Dialog("Identity Confirmation",
                            None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_NO, gtk.RESPONSE_REJECT,
                             gtk.STOCK_YES, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("Has the user's identity been confirmed? (photo ID? teacher?)"
                          "\n\n{} ({})\nfrom {}".format("XXXFULLNAME",
                                                        self.current_username,
                                                        "XXXSCHOOL"))
        dialog.set_border_width(15)
        dialog.vbox.pack_start(label)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        return response == gtk.RESPONSE_ACCEPT


    def _log(self, *args):
        print "[{}]  {}".format(time.strftime("%H:%M"), " ".join(map(str, args)))


    def _set_message(self, message, good_or_bad):
        msg_type = {GOOD: 'OK: {}',
                    BAD: 'NOPE: {}',
                    NEITHER: '{}'}[good_or_bad]

        color = {GOOD: good_message_color,
                 BAD: bad_message_color,
                 NEITHER: neither_message_color}[good_or_bad]
        message = msg_type.format(unicode(message))
        self._msg_lbl.set_text(message)
        self._msg_event.modify_bg(gtk.STATE_NORMAL, color)
        self._log(message)


    def _buttons(self, wristband, abort, manual):
        def set_button(btn, val):
            if val is not None:
                btn.set_sensitive(bool(val))
        set_button(self._wristband_btn, wristband)
        set_button(self._abort_btn, abort)
        set_button(self._manual_btn, manual)
        set_button(self._manual_entry, manual)


    def _error_state(self, message):
        self._set_message(message, BAD)
        self._buttons(False, True, False)


    def _wristband_state(self, message):
        self._can_scan = False
        self._set_message(message, GOOD)
        self._buttons(True, True, False)


    def _ready_state(self):
        self._can_scan = True
        self._set_message("Ready.", NEITHER)
        self._buttons(False, False, True)
        self.current_username = None


    def _construct_page(self):

        # zbar panel setup
        self.zbar = zbarpygtk.Gtk()
        self.zbar.connect("decoded-text", self._decoded)
        self.zbar.set_video_device(self.vdev)
        self.zbar.set_video_enabled(True)
        self.zbar.set_size_request(*SIZE)

        hbox = gtk.HBox(spacing=10)
        vbox = gtk.VBox(spacing=10)
        hbox.add(self.zbar)
        hbox.add(vbox)

        # message area
        self._msg_event = gtk.EventBox()
        self._msg_lbl = gtk.Label("MSG")
        self._msg_lbl.set_width_chars(35)
        self._msg_lbl.set_line_wrap(True)
        self._msg_event.add(self._msg_lbl)
        vbox.add(self._msg_event)

        # wristband and abort buttons
        self._wristband_btn = gtk.Button("WRISTBANDED\n(wristband crimped on user)")
        self._wristband_btn.connect("clicked", self._wristband_click)
        vbox.add(self._wristband_btn)

        self._abort_btn = gtk.Button("ABORT\n(forget current user)")
        self._abort_btn.connect("clicked", self._abort_click)
        vbox.add(self._abort_btn)

        # cheeky spacing
        vbox.add(gtk.Label(""))

        # another vbox to squash some parts of the manual check area
        vbox2 = gtk.VBox(spacing=10)
        vbox2.add(gtk.Label(""))
        vbox2.add(gtk.Label("Manually Check username:"))

        self._manual_entry = gtk.Entry()
        self._manual_entry.connect("activate", self._manual_click)
        vbox2.add(self._manual_entry)

        self._manual_btn = gtk.Button("Check")
        self._manual_btn.connect("clicked", self._manual_click)
        vbox2.add(self._manual_btn)
        vbox.add(vbox2)

        return hbox


    def __init__(self, vdev):
        self.vdev = vdev
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()

        self.window = gtk.Window()
        self.window.set_title("SR Ticket Scanner")
        self.window.set_border_width(10)
        self.window.connect("destroy", gtk.main_quit)

        self.window.add(self._construct_page())
        self.window.show_all()

        # enter the ready state
        self._ready_state()


    def main(self):
        gtk.main()
        gtk.gdk.threads_leave()


if __name__ == "__main__":
    vdev = None
    if len(sys.argv) > 1:
        vdev = sys.argv[1]
    else:
        print "Usage: scanner.py [video-device]"
        exit(1)

    ts = TicketScanner(vdev)
    ts.main()
