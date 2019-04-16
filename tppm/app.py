# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

import os.path
from operator import itemgetter

import arrow

import six.moves.tkinter as Tk
import six.moves.tkinter_messagebox as tk_messagebox
from six import itervalues
from six.moves import filter, map

from trakt import Trakt
from trakt.objects import Episode, Movie, Show

from . import auth
from .dialogs import AuthDialog, MainScreen
from .ui import (
    BusyManager,
    center_toplevel,
    set_icon
)

__version__ = '0.7'

TRAKT_APP = {
    'name': 'Playback Progress Manager',
    'version': __version__,
    'id': '11664'
}
TRAKT_CLIENT = {
    'id': '907c2fe5ff19a529456c0058d2c96f6913f62b55fc6e9a86605f05a0c4e2fec7',
    'secret': '0b70b2072730e0e2ab845f8f89fbfa4a808f47e10678365cb746f4b81fbb56a3'
}

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
        self.main_tk.title('Trakt.tv Playback Progress Remover')
        set_icon(self.main_tk)

        self.busyman = BusyManager(self.main_tk)

        self.main_win = MainScreen(self.main_tk, self)
        center_toplevel(self.main_tk)

        opened = self.show_auth_window()

        self.busyman.busy()

        if self.authorization and not opened:
            self.update_user_info()
            self.refresh_list()

        self.busyman.unbusy()

        self.main_tk.mainloop()

    def stop_currently_playing(self):
        playing = Trakt.http.get('users/me/watching')
        if not playing.status_code == 200:
            tk_messagebox.showinfo('Message', 'Nothing is playing right now.')
            return False

        playing = playing.json()

        def progress():
            expires = arrow.get(playing['expires_at']).timestamp
            started = arrow.get(playing['started_at']).timestamp
            now = arrow.utcnow().timestamp

            watched = now - started
            total = expires - started
            return (watched / total) * 100

        itemType = playing['type']
        params = {
            'progress': progress(),
            itemType: {
                'ids': {
                    'trakt': playing[itemType]['ids']['trakt'],
                }
            }
        }
        Trakt['scrobble'].pause(**params)

        if playing['type'] == 'episode':
            itemInfo = '{0[show][title]} {0[episode][season]}x{0[episode][number]} "{0[episode][title]}"'.format(playing)
        elif playing['type'] == 'movie':
            itemInfo = '{0[movie][title]} ({0[movie][year]})'.format(playing)
        else:
            itemInfo = '(Unknown)'

        tk_messagebox.showinfo(
            'Message',
            'Ok. Current playing {0}:\n{1}\nstopped at {2}%.'.format(
                itemType,
                itemInfo,
                int(params['progress'])
            )
        )

    def _fetch_list(self):
        if not self.authorization:
            tk_messagebox.showwarning('Error', 'Authentication required.')
            raise auth.NotAuthenticatedError()

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
            try:
                self.playback_ids = self._fetch_list()
            except auth.NotAuthenticatedError:
                self.playback_ids = []
                return False

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
        # TODO: Make more DRY.

        if len(newinfo) == 1:
            paused_at = arrow.get(newinfo[0].paused_at).to('local').format('YYYY-MM-DD HH:mm:ss ZZ')

            if isinstance(newinfo[0], Episode):
                self.main_win.lbl_showName.set('Show:')
                self.main_win.lbl_season.set('Season:')
                self.main_win.lbl_episode.set('Episode:')
                self.main_win.lbl_episodeTitle.set('Title:')

                self.main_win.txt_ID.set(newinfo[0].id)
                self.main_win.txt_paused_at.set(paused_at)
                self.main_win.txt_progress.set('%0.f%%' % newinfo[0].progress)
                self.main_win.txt_showName.set(newinfo[0].show.title)
                self.main_win.txt_season.set(newinfo[0].pk[0])
                self.main_win._txtEpisode.grid()
                self.main_win.txt_episode.set(newinfo[0].pk[1])
                self.main_win._txtTitle.grid()
                self.main_win.txt_title.set(newinfo[0].title)

            elif isinstance(newinfo[0], Movie):
                self.main_win.lbl_showName.set('Title:')
                self.main_win.lbl_season.set('Year:')
                self.main_win.lbl_episode.set('')
                self.main_win.lbl_episodeTitle.set('')

                self.main_win.txt_ID.set(newinfo[0].id)
                self.main_win.txt_paused_at.set(paused_at)
                self.main_win.txt_progress.set('%0.f%%' % newinfo[0].progress)
                self.main_win.txt_showName.set(newinfo[0].title)
                self.main_win.txt_season.set(newinfo[0].year)
                self.main_win.txt_episode.set('')
                self.main_win._txtEpisode.grid_remove()
                self.main_win.txt_title.set('')
                self.main_win._txtTitle.grid_remove()

        elif len(newinfo) == 0:
            self.main_win.lbl_showName.set('Show:')
            self.main_win.lbl_season.set('Season:')
            self.main_win.lbl_episode.set('Episode:')
            self.main_win.lbl_episodeTitle.set('Title:')

            self.main_win.txt_ID.set('')
            self.main_win.txt_paused_at.set('')
            self.main_win.txt_progress.set('')
            self.main_win.txt_showName.set('')
            self.main_win.txt_season.set('')
            self.main_win._txtEpisode.grid()
            self.main_win.txt_episode.set('')
            self.main_win._txtTitle.grid()
            self.main_win.txt_title.set('')

        else:  # more than one
            self.main_win.lbl_showName.set('Show:')
            self.main_win.lbl_season.set('Season:')
            self.main_win.lbl_episode.set('Episode:')
            self.main_win.lbl_episodeTitle.set('Title:')

            self.main_win.txt_ID.set('<Multiple>')
            self.main_win.txt_paused_at.set('<Multiple>')
            self.main_win.txt_progress.set('<Multiple>')
            self.main_win.txt_showName.set('<Multiple>')
            self.main_win.txt_season.set('<Multiple>')
            self.main_win._txtEpisode.grid()
            self.main_win.txt_episode.set('<Multiple>')
            self.main_win._txtTitle.grid()
            self.main_win.txt_title.set('<Multiple>')

    def show_auth_window(self):
        """ Create and display an Auth window if not authed. """
        if not self.authorization:
            self.main_win.toggle_auth_button(True)
            self.main_win.lbl_loggedin.set('Not logged in.')

            diag_root = Tk.Toplevel(self.main_tk, {'name': 'auth_window'})
            diag_root.grab_set()
            self.busyman.busy()
            self.busyman.unbusy(diag_root)

            AuthDialog(diag_root, self)
            center_toplevel(diag_root)

            self.main_tk.wait_window(diag_root)

            self.main_tk.grab_release()
            self.busyman.unbusy()
            return True
        return False

    def _on_token_refreshed(self, username, response):
        """ OAuth token refreshed, save tokens for future calls. """
        self.authorization = (response, username)

    def update_user_info(self):
        """
        Updates the authed username (and full name if present)
        """
        if not self.authorization:
            self.main_win.toggle_auth_button(True)
            self.main_win.lbl_loggedin.set('Not logged in.')
            return

        user_settings = Trakt['users/settings'].get()
        self.username = user_settings['user']['username']
        self.fullname = user_settings['user']['name']

        text = 'Logged in as: {0}'.format(self.username)
        if self.fullname not in ('', self.username):
            text += ' ({0})'.format(self.fullname)

        self.main_win.toggle_auth_button(False)
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
