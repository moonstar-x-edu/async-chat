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

        # Declarations
        users_lb = ttk.Label(mainframe, text='Users available: ')
        rooms_lb = ttk.Label(mainframe, text='Rooms available: ')

        user_lbx = Listbox(mainframe, height=10)
        chat_text = Text(mainframe, width=40, height=10)
        room_lbx = Listbox(mainframe, height=5)

        user_entry = ttk.Entry(mainframe)

        send_icon = PhotoImage(file=os.path.abspath(f'{CURRENT_DIRECTORY}/../assets/send.png'))
        #image1 = Image.open(os.path.abspath(f'{CURRENT_DIRECTORY}/../assets/right-arrow.png'))
        # image1 = image1.resize((10, 10), Image.ANTIALIAS)

        # test = ImageTk.PhotoImage(Image.open(os.path.abspath(f'{CURRENT_DIRECTORY}/../assets/right-arrow.png')).resize((20, 20), Image.ANTIALIAS))
        send_lb = ttk.Label(mainframe, text='merengues')
        #send_lb['image'] = test
        #send_lb['text'] = 'holis'
        #send_lb['text'] = 'Hola'


        #image = PhotoImage(file='right-arrow.jpg')
        #send_lb['image'] = image

        #Postioning
        users_lb.grid(column=0, row=0)
        rooms_lb.grid(column=0, row=2)
        user_lbx.grid(column=0, row=1)
        chat_text.grid(column=1, row=1, columnspan=3)
        room_lbx.grid(column=0, row=3)
        user_entry.grid(column=1, row=3, sticky=(W))

        send_lb.grid(column=5, row=5)