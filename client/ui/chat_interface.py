from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

import os

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ChatInterface:

    def __init__(self, root, client):

        self.client = client
        root.title("Async Chat")

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Images
        self.send_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/send.png')).resize((20, 20)))

        self.choose_file_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/clip.png')).resize((20, 20)))


        # Variable declarations
        self.user_greetings = StringVar()
        self.user_list_example = ["user1", "user2"]
        self.user_list = StringVar(value=self.user_list_example)

        # Widget Declarations
        user_greetings_lb = ttk.Label(self.mainframe, textvariable=self.user_greetings)
        user_greetings_lb.text = self.user_greetings  # prevents garbage collection

        user_lbx = Listbox(self.mainframe, height=10, listvariable=self.user_list)
        start_chat_btn = ttk.Button(self.mainframe, text="Start chat", command=self.onStartChat)

        self.user_list_example.append("user3")
        self.user_list.set(self.user_list_example)


        self.user_greetings.set("Bienvenido, {username xd}!")

        # If enter is pressed, bind to onStartChat
        # root.bind("<Return>", self.onStartChat())

        # Positioning
        user_greetings_lb.grid(column=0, row=0, pady=5, padx=10)
        user_lbx.grid(column=0, row=1)
        start_chat_btn.grid(column=0, row=2)


    def onStartChat(self):
        t = Toplevel(self.mainframe)
        t.title = "Chat room with"

