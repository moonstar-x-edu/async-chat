from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

import os

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ChatInterface:

    def __init__(self, root):

        root.title("Async Chat")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Images
        self.send_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/send.png')).resize((20, 20)))

        self.choose_file_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/clip.png')).resize((20, 20)))

        # Widget Declarations
        users_lb = ttk.Label(mainframe, text='Users available: ')
        rooms_lb = ttk.Label(mainframe, text='Rooms available: ')

        user_lbx = Listbox(mainframe, height=10)
        chat_text = Text(mainframe, width=40, height=10)
        room_lbx = Listbox(mainframe, height=5)

        user_entry = ttk.Entry(mainframe, width=40)

        send_bt = ttk.Button(mainframe, image=self.send_icon)
        send_bt.image = self.send_icon  # prevents garbage collection

        file_bt = ttk.Button(mainframe, image=self.choose_file_icon)
        file_bt.image = self.choose_file_icon

        # Positioning
        users_lb.grid(column=0, row=0, pady=5, padx=15, sticky='w')
        rooms_lb.grid(column=0, row=2, pady=5, padx=15, sticky='w')
        user_lbx.grid(column=0, row=1, padx=10)
        chat_text.grid(column=1, row=1, columnspan=3, rowspan=3, sticky='nsew')
        room_lbx.grid(column=0, row=3, rowspan=2, padx=15)

        user_entry.grid(column=1, row=4, sticky='we')
        send_bt.grid(column=2, row=4, sticky='we')
        file_bt.grid(column=3, row=4, sticky='we')
