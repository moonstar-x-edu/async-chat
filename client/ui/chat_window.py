import os
from pathlib import Path
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ChatWindow:
    def __init__(self, chat_interface, mainframe, peer_username):
        self.chat_interface = chat_interface
        self.client = chat_interface.client
        self.peer_username = peer_username

        self.window = Toplevel(mainframe)
        self.window.title(f"{self.client.username}: Chatting with {peer_username}")
        self.window.resizable(False, False)

        # Send Button
        self.send_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/send.png')).resize((20, 20)))

        send_bt = ttk.Button(self.window, image=self.send_icon, command=self.send_message)
        send_bt.image = self.send_icon  # prevents garbage collection

        # File Button
        self.choose_file_icon = ImageTk.PhotoImage(
            Image.open(os.path.abspath(
                f'{CURRENT_DIRECTORY}/../assets/clip.png')).resize((20, 20)))

        file_bt = ttk.Button(self.window, image=self.choose_file_icon, command=self.send_file)
        file_bt.image = self.choose_file_icon

        # Chatbox
        self.chatbox = Text(self.window, width=30, height=15, borderwidth=2, relief="groove")
        self.chatbox.insert(END, f"Connected to {peer_username}\n")
        self.chatbox['state'] = 'disabled'

        # User Entry
        self.user_entry_value = StringVar()
        user_entry = ttk.Entry(self.window, width=30, textvariable=self.user_entry_value)
        user_entry.bind('<Return>', self.send_message)

        self.chatbox.grid(column=0, row=1, columnspan=3, sticky='nsew', padx=15, pady=(10, 0))
        user_entry.grid(column=0, row=2, sticky='we', padx=(15, 0), pady=(3, 10))
        file_bt.grid(column=1, row=2, sticky='nsew', padx=3, pady=(3, 10))
        send_bt.grid(column=2, row=2, sticky='nsew', padx=(0, 15), pady=(3, 10))

        self._register_window_events()

    def _register_window_events(self):
        self.window.protocol('WM_DELETE_WINDOW', self._close_chat)

    def _close_chat(self):
        self.client.disconnect_from_user(self.peer_username)
        self.chat_interface.destroy_chat_window(self.peer_username)

    def _append_to_chatbox(self, message: str):
        now = datetime.now()
        now_ts = now.strftime('%H:%M:%S')

        self.chatbox['state'] = 'normal'
        self.chatbox.insert(END, f'({now_ts}) {message}\n')
        self.chatbox['state'] = 'disabled'

        self.chatbox.see(END)

    def add_peer_message(self, message: str):
        self._append_to_chatbox(f'{self.peer_username}: {message}')

    def send_message(self, trigger_event=None):
        message = self.user_entry_value.get()

        if len(message) < 1:
            return

        self.user_entry_value.set('')
        self._append_to_chatbox(f'Me: {message}')
        self.client.send_message_to(self.peer_username, message)

    def send_file(self):
        try:
            filetypes = [
                ('All files', '*.*')
            ]

            file_path = filedialog.askopenfilename(title='Open a file', initialdir=Path.home(), filetypes=filetypes)

            if file_path is None or '':
                return

            filename = os.path.basename(file_path)

            self.client.send_file(self.peer_username, filename, file_path)

        except Exception as e:
            messagebox.showerror('Could not upload the file.', str(e))
