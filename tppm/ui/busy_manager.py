# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from six import itervalues
from six.moves.tkinter import TclError


class BusyManager(object):
    # Based on http://effbot.org/zone/tkinter-busy.htm

    def __init__(self, widget):
        self.toplevel = widget.winfo_toplevel()
        self.widgets = {}

    def busy(self, widget=None):
        # attach busy cursor to toplevel, plus all windows
        # that define their own cursor.

        if widget is None:
            w = self.toplevel  # myself
        else:
            w = widget

        if str(w) not in self.widgets:
            # attach cursor to this widget
            cursor = self._get_cursor(w)
            if cursor is not None and cursor != 'watch':
                self.widgets[str(w)] = (w, cursor)
                self._set_cursor(w, 'watch')

        for w in itervalues(w.children):
            self.busy(w)

    def unbusy(self, widget=None):
        # restore cursors
        if widget is not None and str(widget) in self.widgets:
            w, cursor = self.widgets[str(widget)]
            self._set_cursor(w, cursor)
            del self.widgets[str(widget)]

            for w in itervalues(w.children):
                self.unbusy(w)
        else:
            for w, cursor in itervalues(self.widgets):
                self._set_cursor(w, cursor)

            self.widgets = {}

    @staticmethod
    def _get_cursor(widget):
        try:
            return widget.cget('cursor')
        except TclError:
            return None

    @staticmethod
    def _set_cursor(widget, cursor):
        try:
            widget.config(cursor=cursor)
        except TclError:
            pass
