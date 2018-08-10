# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

import os.path
import webbrowser
from operator import itemgetter

import six.moves.tkinter as Tk
import six.moves.tkinter_messagebox as tk_messagebox
from six import itervalues
from six.moves import filter, map

from trakt import Trakt
from trakt.objects import Episode, Movie, Show

from . import auth
from .ui import (
    AuthUI,
    BusyManager,
    center_toplevel,
    MainUI,
    set_icon
)

__version__ = '0.6'

TRAKT_APP = {
    'name': 'Playback Progress Manager',
    'version': __version__,
    'id': '11664'
}
TRAKT_CLIENT = {
    'id': '907c2fe5ff19a529456c0058d2c96f6913f62b55fc6e9a86605f05a0c4e2fec7',
    'secret': '0b70b2072730e0e2ab845f8f89fbfa4a808f47e10678365cb746f4b81fbb56a3'
}


class AuthDialog(AuthUI):
    """ Auth UI extension """

    def button_get_code_command(self):
        """ When user clicks Get Code button. """
        # Request authentication
        webbrowser.open_new_tab(Trakt['oauth/pin'].url())

        # Disable PIN button
        self._button_get_code['state'] = 'disabled'

        # Enable textbox and done button
        self._entry_code['state'] = 'normal'
        self._button_done['state'] = 'normal'

    def button_done_command(self):
        """
        When user has clicked 'Done'
        after completing auth process
        """
        # Exchange `code` for `access_token`
        pin = self.pin_code.get()
        if len(pin) != 8:
            tk_messagebox.showwarning('Warning', 'The PIN code is invalid.', parent=self.parent)
            return False
        self.root.authorization = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')

        if not self.root.authorization:
            tk_messagebox.showwarning('Warning', 'Login unsuccessful.', parent=self.parent)
            self.destroy()
        else:
            tk_messagebox.showinfo('Message', 'Login successful.', parent=self.parent)
            self.destroy()

            self.root.update_user_info()
            self.root.refresh_list()

    def destroy(self):
        # Return to MainScreen
        self.parent.destroy()
        self.root.main_tk.focus_set()


class MainScreen(MainUI):
    """ Main UI extension """

    # Auth & Login
    def hide_auth_button(self):
        """ Hide auth button """
        self._btnLogin.grid_forget()

    def _btn_login_command(self):
        self.root.show_auth_window()

    # Refresh
    def _btn_refresh_command(self):
        self.root.busyman.busy()
        self.root.refresh_list()
        self.root.update_info([])
        self.root.busyman.unbusy()

    # Listbox
    def listbox_insert(self, index, elements):
        """ Inserts items to the Listbox """
        self._listbox.insert(index, *elements)

    def listbox_clear_all(self):
        """ Removes all of the Listbox's items """
        self._listbox.delete(0, Tk.END)

    def _listbox_onselect(self, event):
        selection = event.widget.curselection()
        self.root.update_info([
            self.root.playback_ids[index][1]
            for index in selection
        ])

    # (De)Select All
    def _btn_toggle_selection_command(self):
        multiple = len(self._listbox.curselection()) > 1
        action = 'selection_clear' if multiple else 'selection_set'
        getattr(self._listbox, action)(0, Tk.END)
        self._listbox.event_generate('<<ListboxSelect>>')

    # Remove
    def _btn_remove_selected_command(self):
        if not self.root.authorization:
            tk_messagebox.showwarning('Error', 'Authentication required.')
            return False

        listbox = self._listbox
        selection = listbox.curselection()
        count = len(selection)
        if not count:
            return False

        confirm = tk_messagebox.askyesno(
            'Confirm action',
            'Are you sure you want to remove {many}the'
            ' selected item{plural} from your Trakt database?'.format(
                many='all of ' if count > 1 else '',
                plural='s' if count > 1 else ''
            )
        )
        if not confirm:
            return False

        self.root.busyman.busy()

        failed_at = None
        removed_count = 0
        for list_index in reversed(selection):
            current = self.root.playback_ids[list_index]
            response = Trakt['sync/playback'].delete(current[0])
            if not response:
                failed_at = current
                break
            self.root.playback_ids.pop(list_index)
            removed_count += 1

        if failed_at is not None:
            tk_messagebox.showwarning(
                'Warning',
                'Something went wrong with {id}:\n{item}'.format(
                    id=failed_at[0],
                    item=failed_at[1]
                )
            )
        else:
            tk_messagebox.showinfo(
                'Success',
                '{count} item{plural} removed.'.format(
                    count=removed_count,
                    plural='s' if removed_count > 1 else ''
                )
            )

        self.root.refresh_list(local=True)
        self.root.update_info([])

        self.root.busyman.unbusy()


class Application(object):
    """ Application container """

    auth_filepath = os.path.normpath(os.path.join(
        os.path.dirname(__file__), '..', 'authorization.json'
    ))

    def __init__(self):
        # Trakt client configuration
        Trakt.base_url = 'http://api.trakt.tv'
        Trakt.configuration.defaults.app(**TRAKT_APP)
        Trakt.configuration.defaults.client(**TRAKT_CLIENT)
        # Bind trakt events
        Trakt.on('oauth.refresh', self._on_token_refreshed)

        self.main_tk = None
        self.main_win = None

        self._authorization = None
        self.username = None
        self.fullname = None
        self.playback_ids = []

    def main(self):
        """ Run main application """
        self.main_tk = Tk.Tk()
        self.main_win = MainScreen(self.main_tk, self)
        set_icon(self.main_tk)
        center_toplevel(self.main_tk)

        self.busyman = BusyManager(self.main_tk)

        if self.authorization:
            self.busyman.busy()
            self.update_user_info()
            self.refresh_list()
            self.busyman.unbusy()

        self.main_tk.update()
        self.show_auth_window()

        self.main_tk.mainloop()

    def _fetch_list(self):
        if not self.authorization:
            tk_messagebox.showwarning('Error', 'Authentication required.')
            return []

        def make_items(data):
            for obj in itervalues(playback):
                if isinstance(obj, Show):
                    for (_sk, _ek), episode in obj.episodes():
                        yield (episode.id, episode)
                elif isinstance(obj, Movie):
                    yield (obj.id, obj)

        # Fetch playback
        playback = Trakt['sync/playback'].get(exceptions=True)

        return list(make_items(playback))

    def refresh_list(self, local=False):
        """
        Refreshes the Listbox with items, source depends on the value of `local`

        :param local: if False, uses Trakt.tv's database, otherwise uses the playback_ids array
        """
        self.main_win.listbox_clear_all()  # Clear
        if not local:
            self.playback_ids = self._fetch_list()

        if not self.playback_ids:
            if not local:
                tk_messagebox.showinfo('Message', 'There are no items to remove.')
            return True

        def make_list_item(idx, item):
            if isinstance(item, Episode):
                return '{id:03d}. {show}: S{se:02d}E{ep:02d} ({title})'.format(
                    id=idx,
                    show=item.show.title,
                    se=item.pk[0],
                    ep=item.pk[1],
                    title=item.title
                )
            elif isinstance(item, Movie):
                return '{id:03d}. {title} ({year})'.format(
                    id=idx,
                    title=item.title,
                    year=item.year
                )
            else:
                return None

        # populate list
        generator = map(itemgetter(1), self.playback_ids)
        list_items = filter(None, [
            make_list_item(idx, item)
            for idx, item in enumerate(generator, 1)
        ])
        self.main_win.listbox_insert(Tk.END, list_items)

    def update_info(self, newinfo):
        """
        Updates the selected item info displayed in labels and textboxes.

        :param newinfo: Episode or Movie item from playback_ids
        """
        if len(newinfo) == 1:
            if isinstance(newinfo[0], Episode):
                self.main_win.lbl_showName.set('Show:')
                self.main_win.lbl_season.set('Season:')
                self.main_win.lbl_episode.set('Episode:')
                self.main_win.lbl_episodeTitle.set('Title:')

                self.main_win.txt_ID.set(newinfo[0].id)
                self.main_win.txt_progress.set('%0.f%%' % newinfo[0].progress)
                self.main_win.txt_showName.set(newinfo[0].show.title)
                self.main_win.txt_season.set(newinfo[0].pk[0])
                self.main_win.txt_episode.set(newinfo[0].pk[1])
                self.main_win.txt_title.set(newinfo[0].title)

            elif isinstance(newinfo[0], Movie):
                self.main_win.lbl_showName.set('Title:')
                self.main_win.lbl_season.set('Year:')
                self.main_win.lbl_episode.set('')
                self.main_win.lbl_episodeTitle.set('')

                self.main_win.txt_ID.set(newinfo[0].id)
                self.main_win.txt_progress.set('%0.f%%' % newinfo[0].progress)
                self.main_win.txt_showName.set(newinfo[0].title)
                self.main_win.txt_season.set(newinfo[0].year)
                self.main_win.txt_episode.set('')
                self.main_win.txt_title.set('')

        elif len(newinfo) == 0:
            self.main_win.lbl_showName.set('Show:')
            self.main_win.lbl_season.set('Season:')
            self.main_win.lbl_episode.set('Episode:')
            self.main_win.lbl_episodeTitle.set('Title:')

            self.main_win.txt_ID.set('')
            self.main_win.txt_progress.set('')
            self.main_win.txt_showName.set('')
            self.main_win.txt_season.set('')
            self.main_win.txt_episode.set('')
            self.main_win.txt_title.set('')

        else:  # more than one
            self.main_win.lbl_showName.set('Show:')
            self.main_win.lbl_season.set('Season:')
            self.main_win.lbl_episode.set('Episode:')
            self.main_win.lbl_episodeTitle.set('Title:')

            self.main_win.txt_ID.set('<Multiple>')
            self.main_win.txt_progress.set('<Multiple>')
            self.main_win.txt_showName.set('<Multiple>')
            self.main_win.txt_season.set('<Multiple>')
            self.main_win.txt_episode.set('<Multiple>')
            self.main_win.txt_title.set('<Multiple>')

    def show_auth_window(self):
        """ Create and display an Auth window if not authed. """
        if not self.authorization:
            diag_root = Tk.Toplevel(self.main_tk, {'name': 'auth_window'})
            diag_root.grab_set()
            self.busyman.busy()
            self.busyman.unbusy(diag_root)

            AuthDialog(diag_root, self)
            center_toplevel(diag_root)

            self.main_tk.wait_window(diag_root)

            self.main_tk.grab_release()
            self.busyman.unbusy()

    def _on_token_refreshed(self, username, response):
        """ OAuth token refreshed, save tokens for future calls. """
        self.authorization = (response, username)

    def update_user_info(self):
        """
        Updates the authed username (and full name if present)
        """
        if not self.authorization:
            self.main_win.lbl_loggedin.set('Not logged in.')
            return

        self.main_win.hide_auth_button()

        user_settings = Trakt['users/settings'].get()
        self.username = user_settings['user']['username']
        self.fullname = user_settings['user']['name']

        text = 'Logged in as: {0}'.format(self.username)
        if self.fullname not in ('', self.username):
            text += ' ({1})'.format(self.fullname)

        self.main_win.lbl_loggedin.set(text)

    @property
    def authorization(self):
        if not self._authorization:
            auth_data = auth.load(self.auth_filepath)
            self._update_auth(auth_data)

        return bool(self._authorization)

    @authorization.setter
    def authorization(self, data):
        if not data:
            return

        try:
            data, username = data
        except ValueError:
            username = None

        self._update_auth(data, username)
        auth.save(self.auth_filepath, data)

    def _update_auth(self, data, username=None):
        self._authorization = data
        if not data:
            return

        Trakt.configuration.defaults.oauth.from_response(
            response=data,
            refresh=True,
            username=username
        )


def main():
    root = Application()
    root.main()
