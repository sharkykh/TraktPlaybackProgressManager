from Tkinter import *


# noinspection PyUnresolvedReferences,SpellCheckingInspection
class MainUI(object):
    def __init__(self, parent, app):
        self.top = parent
        parent.title('Trakt.tv Playback Progress Remover')

        self.parent = parent
        self.root = app

        self.selectedStatus = False

        # Widget Initialization
        self._listbox = Listbox(
            parent,
            font="{Segoe UI} 10",
            height=0,
            selectmode="extended",
            state="normal",
            cursor="hand2",
        )
        self._label_header = Label(
            parent,
            font="{Segoe UI} 16 bold",
            text="Playback items available for removal",
        )
        self._label_actions = Label(
            parent,
            font="{Segoe UI} 14 bold",
            text="Actions",
        )
        self._label_info = Label(
            parent,
            font="{Segoe UI} 14 bold",
            text="Info",
        )
        self._btnRefresh = Button(
            parent,
            font="{Segoe UI} 12 bold",
            text="Refresh",
        )
        self._btnRemoveSelected = Button(
            parent,
            font="{Segoe UI} 12 bold",
            wraplength=120,
            text="Remove Selected",
        )
        self._btnSelectDeselectAll = Button(
            parent,
            font="{Segoe UI} 12 bold",
            wraplength=120,
            text="Select / Deselect All",
        )
        self._btnLogin = Button(
            parent,
            font="{Segoe UI} 12 bold",
            text="Login/Auth",
        )
        self._lbl_ID = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="ID:",
        )
        self._lbl_Progress = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="Progress:",
        )
        self.lbl_showName = StringVar(value="Show:")
        self._lbl_Show = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_showName,
        )
        self.lbl_season = StringVar(value="Season:")
        self._lbl_Season = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_season,
        )
        self.lbl_episode = StringVar(value="Episode:")
        self._lbl_Episode = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_episode,
        )
        self.lbl_episodeTitle = StringVar(value="Title:")
        self._lbl_Title = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_episodeTitle,
        )
        self.txt_ID = StringVar()
        self._txtID = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_ID,
            width=0,
        )
        self.txt_progress = StringVar()
        self._txtProgress = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_progress,
            width=0,
        )
        self.txt_showName = StringVar()
        self._txtShowName = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_showName,
            width=0,
        )
        self.txt_season = StringVar()
        self._txtSeason = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_season,
            width=0,
        )
        self.txt_episode = StringVar()
        self._txtEpisode = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_episode,
            width=0,
        )
        self.txt_title = StringVar()
        self._txtTitle = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_title,
            width=0,
        )
        self.lbl_loggedin = StringVar(value="Not logged in.")
        self._lbl_loggedin = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_loggedin,
        )

        # widget commands
        self._listbox.bind('<<ListboxSelect>>', self._listbox_onselect)
        self._btnRefresh.configure(
            command=self._btn_refresh_command
        )
        self._btnRemoveSelected.configure(
            command=self._btn_remove_selected_command
        )
        self._btnSelectDeselectAll.configure(
            command=self._btn_toggle_selection_command
        )
        self._btnLogin.configure(
            command=self._btn_login_command
        )

        # Geometry Management
        self._listbox.grid(
            in_=parent,
            column=3,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=5,
            rowspan=7,
            sticky="nsew"
        )
        self._label_header.grid(
            in_=parent,
            column=3,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._label_actions.grid(
            in_=parent,
            column=4,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._label_info.grid(
            in_=parent,
            column=1,
            row=1,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._btnRefresh.grid(
            in_=parent,
            column=4,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=2,
            sticky=""
        )
        self._btnRemoveSelected.grid(
            in_=parent,
            column=4,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=2,
            sticky=""
        )
        self._btnSelectDeselectAll.grid(
            in_=parent,
            column=4,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=2,
            sticky=""
        )
        self._btnLogin.grid(
            in_=parent,
            column=4,
            row=7,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=5,
            rowspan=2,
            sticky="es"
        )
        self._lbl_ID.grid(
            in_=parent,
            column=1,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Progress.grid(
            in_=parent,
            column=1,
            row=3,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Show.grid(
            in_=parent,
            column=1,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Season.grid(
            in_=parent,
            column=1,
            row=5,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Episode.grid(
            in_=parent,
            column=1,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Title.grid(
            in_=parent,
            column=1,
            row=7,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtID.grid(
            in_=parent,
            column=2,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtProgress.grid(
            in_=parent,
            column=2,
            row=3,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtShowName.grid(
            in_=parent,
            column=2,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtSeason.grid(
            in_=parent,
            column=2,
            row=5,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtEpisode.grid(
            in_=parent,
            column=2,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtTitle.grid(
            in_=parent,
            column=2,
            row=7,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_loggedin.grid(
            in_=parent,
            column=1,
            row=8,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=5,
            rowspan=1,
            sticky="sw"
        )

        # Resize Behavior
        parent.resizable(False, False)
        parent.grid_rowconfigure(1, weight=0, minsize=30, pad=20)
        parent.grid_rowconfigure(2, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(3, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(4, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(5, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(6, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(7, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(8, weight=0, minsize=200, pad=0)
        parent.grid_columnconfigure(1, weight=0, minsize=70, pad=5)
        parent.grid_columnconfigure(2, weight=0, minsize=450, pad=0)
        parent.grid_columnconfigure(3, weight=0, minsize=450, pad=0)
        parent.grid_columnconfigure(4, weight=0, minsize=120, pad=0)


# noinspection PyUnresolvedReferences,SpellCheckingInspection
class AuthUI(object):
    def __init__(self, parent, app):
        self.top = parent
        parent.title('Auth window')

        self.parent = parent
        self.root = app

        # Widget Initialization
        self._label_header = Label(
            parent,
            font="{Segoe UI} 20 bold",
            foreground="#ff0000",
            text="Trakt Account Authorization",
        )
        self._button_get_code = Button(
            parent,
            font="{MS Sans Serif} 12 bold",
            text="Get PIN Code",
        )
        self._label_enter_code = Label(
            parent,
            font="{MS Sans Serif} 14",
            text="Enter the code:",
        )
        self._label_click = Label(
            parent,
            font="{MS Sans Serif} 14",
            text="Click the button to get a code:",
        )
        self.pin_code = StringVar()
        self._entry_code = Entry(
            parent,
            font="{MS Sans Serif} 14 bold",
            width=10,
            justify="center",
            textvariable=self.pin_code,
            state="disabled",
        )
        self._button_done = Button(
            parent,
            borderwidth=3,
            font="{MS Sans Serif} 12 bold",
            text="Done",
            state="disabled",
        )

        # widget commands
        self._button_get_code.configure(
            command=self.button_get_code_command
        )
        self._button_done.configure(
            command=self.button_done_command
        )

        # Geometry Management
        self._label_header.grid(
            in_=parent,
            column=1,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="ew"
        )
        self._label_click.grid(
            in_=parent,
            column=1,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._button_get_code.grid(
            in_=parent,
            column=1,
            row=3,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._label_enter_code.grid(
            in_=parent,
            column=1,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._entry_code.grid(
            in_=parent,
            column=1,
            row=5,
            columnspan=1,
            ipadx=5,
            ipady=0,
            padx=5,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._button_done.grid(
            in_=parent,
            column=1,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )

        # Resize Behavior
        parent.resizable(False, False)
        parent.grid_rowconfigure(1, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(2, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(3, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(4, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(5, weight=1, minsize=50, pad=10)
        parent.grid_rowconfigure(6, weight=1, minsize=50, pad=10)
        parent.grid_columnconfigure(1, weight=1, minsize=0, pad=10)
