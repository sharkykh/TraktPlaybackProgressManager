import Tkinter as tk
import tkMessageBox
import webbrowser
from ui import MainUI, AuthUI

from time import sleep
import json
import os.path
import threading

from trakt import Trakt
from trakt.objects import Movie, Episode, Show

class AuthDialog(AuthUI):
    def _button_get_code_command(self):
        # Request authentication
        webbrowser.open(Trakt['oauth/pin'].url(), new = 2) # New tab

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
            self.root._update_user_info(self.root.mainApp)
            self.root.update_list(self.root.mainApp)
        self.root.Tk.focus_set()
        self.top.destroy()

class MainScreen(MainUI):

    def _btnLogin_command(self, *args):
        self.root._authenticate()
    
    def _btnRefresh_command(self, *args):
        self._listbox.delete(0, tk.END) # Clear
        self.root.update_list(self)

    def _btnRemoveSelected_command(self, *args):
        if not self.root.authorization:
            tkMessageBox.showwarning('Error', 'Authentication required.')
            return False
        
        lb = self._listbox
        selection = lb.curselection()
        if len(selection) >= 1:
            yesno = tkMessageBox.askyesno("Message", "Are you sure you want to remove all of\nthe selected item(s) from your Trakt database?")
            if yesno:
                ok = [True, None]        
                with Trakt.configuration.oauth.from_response(self.root.authorization):
                    for idx in selection:
                        response = Trakt['sync/playback'].delete_progress(self.root.playback_ids[idx][0])
                        if not response:
                            ok = [False, self.root.playback_ids[idx]]
                            break
                        lb.delete(idx) # remove from list
                    if not ok[0]:
                        tkMessageBox.showwarning('Warning', 'Something went wrong with\n%r.' % ok[1])
                    else:
                        tkMessageBox.showinfo('Message', 'Items removed.')

    def _btnSelectDeselectAll_command(self, *args):
        if self.selectedStatus is None or self.selectedStatus == False: # Deselected
            self._listbox.selection_set(0, tk.END) # select all
            self.selectedStatus = True
        else: # Selected
            self._listbox.selection_clear(0, tk.END) # deselect all
            self.selectedStatus = False
        self._listbox.event_generate("<<ListboxSelect>>")

    def _listbox_OnSelect(self, event):        
        w = event.widget
        
        newinfo = []
        count = len(w.curselection())
        if count >= 1:
            self.selectedStatus = True
        else:
            self.selectedStatus = False

        for x in range(0, count):
            index = int(w.curselection()[x])
            newinfo.append(self.root.playback_ids[index][1])
        self.root.update_info(self, newinfo)

class Application(object):
    def __init__(self):
        # Trakt client configuration
        Trakt.base_url = 'http://api.trakt.tv'
        
        Trakt.configuration.defaults.app(
            id='11664'
        )
        
        Trakt.configuration.defaults.client(
            id='907c2fe5ff19a529456c0058d2c96f6913f62b55fc6e9a86605f05a0c4e2fec7',
            secret='0b70b2072730e0e2ab845f8f89fbfa4a808f47e10678365cb746f4b81fbb56a3'
        )

        self.authorization = None
        self.username = None
        self.fullname = None
        self.auth_filename = 'authorization.json'
        self.playback_ids = []

        self.mainInterface = None

        # Bind trakt events
        Trakt.on('oauth.token_refreshed', self._on_token_refreshed)

    def main(self):
        self.Tk = tk.Tk()
        self.mainApp = MainScreen(self.Tk, self)

        if self.check_auth():
            self._update_user_info(self.mainApp)
            self.update_list(self.mainApp)
        
        self.Tk.update()

        if not self.check_auth():
            sleep(0.5)
            authDiag = AuthDialog(tk.Toplevel(self.Tk), self)
            self.Tk.wait_window(authDiag.top)

        self.Tk.mainloop()
        

    def update_list(self, mainInterface):
        self.playback_ids = []
        if not self.authorization:
            tkMessageBox.showwarning('Error', 'Authentication required.')
            return False
        
        with Trakt.configuration.oauth.from_response(self.authorization):
            # Fetch playback
            playback = Trakt['sync/playback'].get(exceptions=True)
            for key, item in playback.items():
                if type(item) is Show:
                    for (sk, ek), episode in item.episodes():
                        self.playback_ids.append([episode.id, episode])
                elif type(item) is Movie:
                    self.playback_ids.append([item.id, item])
                
            if not self.playback_ids:
                tkMessageBox.showinfo('Message', 'There are no items to remove.')
                return True

            idx = 1
            cpy_playback = list(self.playback_ids)
            cpy_playback.reverse()
            while cpy_playback:
                listItem = ''
                pbid, item = cpy_playback.pop()
                if type(item) is Episode:
                    listItem = '%d. %s: S%02dE%02d (%s)' % (idx, item.show.title, item.pk[0], item.pk[1], item.title)
                elif type(item) is Movie:
                    listItem = '%d. %s (%s)' % (idx, item.title, item.year)
                
                mainInterface._listbox.insert(tk.END, listItem)
                idx += 1
    
    def update_info(self, mainInterface, newinfo): # newinfo is an item Episode/Movie object from playback_ids
        if len(newinfo) == 1:
            if type(newinfo[0]) is Episode:
                mainInterface.lbl_showName.set("Show:")
                mainInterface.lbl_season.set("Season:")
                mainInterface.lbl_episode.set("Episode:")
                mainInterface.lbl_episodeTitle.set("Title:")
                
                mainInterface.txt_ID.set(newinfo[0].id)
                mainInterface.txt_progress.set("%0.f%%" % newinfo[0].progress)
                mainInterface.txt_showName.set(newinfo[0].show.title)
                mainInterface.txt_season.set(newinfo[0].pk[0])
                mainInterface.txt_episode.set(newinfo[0].pk[1])
                mainInterface.txt_title.set(newinfo[0].title)
            
            elif type(newinfo[0]) is Movie:
                mainInterface.lbl_showName.set("Title:")
                mainInterface.lbl_season.set("Year:")
                mainInterface.lbl_episode.set("")
                mainInterface.lbl_episodeTitle.set("")

                mainInterface.txt_ID.set(newinfo[0].id)
                mainInterface.txt_progress.set("%0.f%%" % newinfo[0].progress)
                mainInterface.txt_showName.set(newinfo[0].title)
                mainInterface.txt_season.set(newinfo[0].year)
                mainInterface.txt_episode.set("")
                mainInterface.txt_title.set("")
        
        elif len(newinfo) == 0:
            mainInterface.lbl_showName.set("Show:")
            mainInterface.lbl_season.set("Season:")
            mainInterface.lbl_episode.set("Episode:")
            mainInterface.lbl_episodeTitle.set("Title:")

            mainInterface.txt_ID.set("")
            mainInterface.txt_progress.set("")
            mainInterface.txt_showName.set("")
            mainInterface.txt_season.set("")
            mainInterface.txt_episode.set("")
            mainInterface.txt_title.set("")
        
        else: # more than one
            mainInterface.lbl_showName.set("Show:")
            mainInterface.lbl_season.set("Season:")
            mainInterface.lbl_episode.set("Episode:")
            mainInterface.lbl_episodeTitle.set("Title:")

            mainInterface.txt_ID.set("<Multiple>")
            mainInterface.txt_progress.set("<Multiple>")
            mainInterface.txt_showName.set("<Multiple>")
            mainInterface.txt_season.set("<Multiple>")
            mainInterface.txt_episode.set("<Multiple>")
            mainInterface.txt_title.set("<Multiple>")

    def check_auth(self):
        if os.path.isfile(self.auth_filename):
            with open(self.auth_filename) as data_file:
                self.authorization = json.load(data_file)
            return True

    def _authenticate(self):
        if not self.check_auth():
            sleep(0.5)
            authDiag = AuthDialog(tk.Toplevel(self.Tk), self)
            self.Tk.wait_window(authDiag.top)

    def _on_token_refreshed(self, response):
        # OAuth token refreshed, save token for future calls
        self.authorization = response

        with open(self.auth_filename, 'w') as outfile:
            json.dump(self.authorization, outfile)

    def _update_user_info(self, mainInterface):
        if not self.authorization:
            mainInterface.lbl_loggedin.set("Not logged in.")
        else:
            mainInterface._btnLogin.grid_forget()
            with Trakt.configuration.oauth.from_response(self.authorization):
                usersettings = Trakt['users/settings'].get()
                self.username = usersettings['user']['username']
                self.fullname = usersettings['user']['name']
                mainInterface.lbl_loggedin.set("Logged in as: %s (%s)" % (self.username, self.fullname))

def main():
    root = Application()
    root.main()
    
if __name__ == '__main__': main()
