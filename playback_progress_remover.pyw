#pylint: disable=C0111
import json
import os.path
import Tkinter as tk
import tkMessageBox
import webbrowser
from time import sleep

from ui import MainUI, AuthUI

from trakt import Trakt
from trakt.objects import Movie, Episode, Show

class AuthDialog(AuthUI):
    def _button_get_code_command(self):
        # Request authentication
        webbrowser.open(Trakt['oauth/pin'].url(), new=2) # New tab

        # Disable PIN button
        self._button_get_code['state'] = 'disabled'

        # Enable textbox and done button
        self._entry_code['state'] = 'normal'
        self._button_done['state'] = 'normal'

    def _button_done_command(self):
        # Exchange `code` for `access_token`
        pin = self.pin_code.get()
        if len(pin) == 0 or len(pin) > 8:
            tkMessageBox.showwarning('Trakt.authenticate()', 'You didn\'t enter the PIN code.')
            return False
        self.root.authorization = Trakt['oauth'].token_exchange(pin, 'urn:ietf:wg:oauth:2.0:oob')

        if not self.root.authorization:
            tkMessageBox.showwarning('Trakt.authenticate()', 'Auth unsuccessful.')
        else:
            with open('authorization.json', 'w') as outfile:
                json.dump(self.root.authorization, outfile)
            tkMessageBox.showinfo('Trakt.authenticate()', 'Login successful.')
            self.root.update_user_info(self.root.main_app)
            self.root.update_list(self.root.main_app)
        self.root.main_tk.focus_set()
        self.top.destroy()

class MainScreen(MainUI):
    def hide_auth_button(self):
        self._btnLogin.grid_forget()

    def listbox_insert(self, index, *elements):
        self._listbox.insert(index, *elements)

    def _btn_login_command(self):
        self.root.show_auth_window()

    def _btn_refresh_command(self):
        self._listbox.delete(0, tk.END) # Clear
        self.root.update_list(self)

    def _btn_remove_selected_command(self):
        if not self.root.authorization:
            tkMessageBox.showwarning('Error', 'Authentication required.')
            return False

        listbox = self._listbox
        selection = listbox.curselection()
        if len(selection) >= 1:
            yesno = tkMessageBox.askyesno("Message",
                                          "Are you sure you want to remove all of\n"
                                          "the selected item(s) from your Trakt database?")
            if yesno:
                noerror = {'continue': True, 'failed_at': None}
                with Trakt.client.configuration.oauth.from_response(self.root.authorization):
                    for idx in selection:
                        response = Trakt['sync/playback'].delete_progress(
                            self.root.playback_ids[idx][0])
                        if not response:
                            noerror['continue'] = False
                            noerror['failed_at'] = self.root.playback_ids[idx]
                            break
                        listbox.delete(idx) # remove from list
                    if not noerror['continue']:
                        tkMessageBox.showwarning(
                            'Warning',
                            'Something went wrong with\n%r.' % noerror['failed_at'])
                    else:
                        tkMessageBox.showinfo('Message', 'Items removed.')

    def _btn_toggle_selection_command(self):
        if self.selectedStatus is None or not self.selectedStatus: # Deselected
            self._listbox.selection_set(0, tk.END) # select all
            self.selectedStatus = True
        else: # Selected
            self._listbox.selection_clear(0, tk.END) # deselect all
            self.selectedStatus = False
        self._listbox.event_generate("<<ListboxSelect>>")

    def _listbox_onselect(self, event):
        listbox = event.widget

        newinfo = []
        count = len(listbox.curselection())
        if count >= 1:
            self.selectedStatus = True
        else:
            self.selectedStatus = False

        for select_id in range(0, count):
            index = int(listbox.curselection()[select_id])
            newinfo.append(self.root.playback_ids[index][1])
        self.root.update_info(self, newinfo)

class Application(object):
    def __init__(self):
        # Trakt client configuration
        Trakt.base_url = 'http://api.trakt.tv'

        Trakt.client.configuration.defaults.app(
            id='11664'
        )

        Trakt.client.configuration.defaults.client(
            id='907c2fe5ff19a529456c0058d2c96f6913f62b55fc6e9a86605f05a0c4e2fec7',
            secret='0b70b2072730e0e2ab845f8f89fbfa4a808f47e10678365cb746f4b81fbb56a3'
        )

        self.main_tk = None
        self.main_app = None
        self.main_win = None

        self.authorization = None
        self.username = None
        self.fullname = None
        self.auth_filename = 'authorization.json'
        self.playback_ids = []

        # Bind trakt events
        Trakt.client.on('oauth.token_refreshed', self._on_token_refreshed)

    def main(self):
        self.main_tk = tk.Tk()
        self.main_app = MainScreen(self.main_tk, self)

        if self.check_auth():
            self.update_user_info(self.main_app)
            self.update_list(self.main_app)

        self.main_tk.update()

        if not self.check_auth():
            sleep(0.5)
            auth_diag = AuthDialog(tk.Toplevel(self.main_tk), self)
            self.main_tk.wait_window(auth_diag.top)

        self.main_tk.mainloop()


    def update_list(self, main_win):
        self.playback_ids = []
        if not self.authorization:
            tkMessageBox.showwarning('Error', 'Authentication required.')
            return False

        with Trakt.configuration.oauth.from_response(self.authorization):
            # Fetch playback
            playback = Trakt['sync/playback'].get(exceptions=True)
            for _, item in playback.items():
                if isinstance(item) is Show:
                    for (_, _), episode in item.episodes():
                        self.playback_ids.append([episode.id, episode])
                elif isinstance(item) is Movie:
                    self.playback_ids.append([item.id, item])

            if not self.playback_ids:
                tkMessageBox.showinfo('Message', 'There are no items to remove.')
                return True

            idx = 1
            cpy_playback = list(self.playback_ids)
            cpy_playback.reverse()
            while cpy_playback:
                list_item = ''
                _, item = cpy_playback.pop()
                if isinstance(item) is Episode:
                    list_item = '%d. %s: S%02dE%02d (%s)' \
                                % (idx, item.show.title, item.pk[0], item.pk[1], item.title)
                elif isinstance(item) is Movie:
                    list_item = '%d. %s (%s)' \
                                % (idx, item.title, item.year)

                main_win.listbox_insert(tk.END, list_item)
                idx += 1

    def update_info(self, main_win, newinfo):
        # newinfo is an item Episode/Movie object from playback_ids
        if len(newinfo) == 1:
            if isinstance(newinfo[0]) is Episode:
                main_win.lbl_showName.set("Show:")
                main_win.lbl_season.set("Season:")
                main_win.lbl_episode.set("Episode:")
                main_win.lbl_episodeTitle.set("Title:")

                main_win.txt_ID.set(newinfo[0].id)
                main_win.txt_progress.set("%0.f%%" % newinfo[0].progress)
                main_win.txt_showName.set(newinfo[0].show.title)
                main_win.txt_season.set(newinfo[0].pk[0])
                main_win.txt_episode.set(newinfo[0].pk[1])
                main_win.txt_title.set(newinfo[0].title)

            elif isinstance(newinfo[0]) is Movie:
                main_win.lbl_showName.set("Title:")
                main_win.lbl_season.set("Year:")
                main_win.lbl_episode.set("")
                main_win.lbl_episodeTitle.set("")

                main_win.txt_ID.set(newinfo[0].id)
                main_win.txt_progress.set("%0.f%%" % newinfo[0].progress)
                main_win.txt_showName.set(newinfo[0].title)
                main_win.txt_season.set(newinfo[0].year)
                main_win.txt_episode.set("")
                main_win.txt_title.set("")

        elif len(newinfo) == 0:
            main_win.lbl_showName.set("Show:")
            main_win.lbl_season.set("Season:")
            main_win.lbl_episode.set("Episode:")
            main_win.lbl_episodeTitle.set("Title:")

            main_win.txt_ID.set("")
            main_win.txt_progress.set("")
            main_win.txt_showName.set("")
            main_win.txt_season.set("")
            main_win.txt_episode.set("")
            main_win.txt_title.set("")

        else: # more than one
            main_win.lbl_showName.set("Show:")
            main_win.lbl_season.set("Season:")
            main_win.lbl_episode.set("Episode:")
            main_win.lbl_episodeTitle.set("Title:")

            main_win.txt_ID.set("<Multiple>")
            main_win.txt_progress.set("<Multiple>")
            main_win.txt_showName.set("<Multiple>")
            main_win.txt_season.set("<Multiple>")
            main_win.txt_episode.set("<Multiple>")
            main_win.txt_title.set("<Multiple>")

    def check_auth(self):
        if os.path.isfile(self.auth_filename):
            with open(self.auth_filename) as data_file:
                self.authorization = json.load(data_file)
            return True

    def show_auth_window(self):
        if not self.check_auth():
            sleep(0.5)
            auth_diag = AuthDialog(tk.Toplevel(self.main_tk), self)
            self.main_tk.wait_window(auth_diag.top)

    def _on_token_refreshed(self, response):
        # OAuth token refreshed, save token for future calls
        self.authorization = response

        with open(self.auth_filename, 'w') as outfile:
            json.dump(self.authorization, outfile)

    def update_user_info(self, main_win):
        if not self.authorization:
            main_win.lbl_loggedin.set("Not logged in.")
        else:
            main_win.hide_auth_button()
            with Trakt.configuration.oauth.from_response(self.authorization):
                usersettings = Trakt['users/settings'].get()
                self.username = usersettings['user']['username']
                self.fullname = usersettings['user']['name']
                main_win.lbl_loggedin.set("Logged in as: %s (%s)" % (self.username, self.fullname))

def main():
    root = Application()
    root.main()

if __name__ == '__main__':
    main()
