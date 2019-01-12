# coding: utf-8
""" Trakt Playback Manager """
from __future__ import absolute_import
from __future__ import unicode_literals

import webbrowser

import six.moves.tkinter as Tk
import six.moves.tkinter_messagebox as tk_messagebox

from trakt import Trakt

from .ui import AuthUI, MainUI


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

    def _open_repo(self, event):
        confirm = tk_messagebox.askokcancel(
            None,
            'Open the GitHub repository?'
        )
        if not confirm:
            return False

        webbrowser.open_new_tab('https://github.com/sharkykh/TraktPlaybackProgressManager')

    # Auth & Login
    def toggle_auth_button(self, show):
        """ Toggle auth button """
        if show:
            self._btnLogin.grid()
        else:
            self._btnLogin.grid_remove()

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
        one_option = len(self.root.playback_ids) == 1
        multiple = len(self._listbox.curselection()) > (0 if one_option else 1)
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
