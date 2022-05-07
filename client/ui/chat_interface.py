from tkinter import *
from tkinter import ttk, messagebox
from .chat_window import ChatWindow


class ChatInterface:
    def __init__(self, root, client):
        self.client = client

        self.chat_windows = dict()  # peer_username -> ChatWindow

        # Window
        root.title(f"Async Chat - {self.client.username}")

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # User Greeting
        user_greeting = StringVar()
        user_greeting.set(f"Bienvenido, {self.client.username}!")
        user_greetings_label = ttk.Label(self.mainframe, textvariable=user_greeting)
        user_greetings_label.text = user_greeting  # prevents garbage collection

        # Online User List
        self.user_list = StringVar()
        self.user_listbox = Listbox(self.mainframe, height=10, listvariable=self.user_list)

        # Start Chat Button
        start_chat_btn = ttk.Button(self.mainframe, text="Start Chat", command=self._on_start_chat)

        # Refresh List Button
        refresh_list_btn = ttk.Button(self.mainframe, text="Refresh List", command=self._on_refresh_list)

        # Positioning
        user_greetings_label.grid(column=0, row=0, columnspan=2, pady=(10, 0), padx=15)
        self.user_listbox.grid(column=0, row=1, columnspan=2)
        start_chat_btn.grid(column=0, row=2, padx=(15, 0), pady=(3, 10))
        refresh_list_btn.grid(column=1, row=2, padx=(0, 15), pady=(3, 10))

        self._register_client_events()
        self.client.request_list()

    def _register_client_events(self):
        self.client.emitter.on('list', self._handle_user_list)
        self.client.emitter.on('message', self._handle_message)
        self.client.emitter.on('connect', self._handle_connect)
        self.client.emitter.on('disconnect', self._handle_disconnect)

    def _handle_user_list(self, users_online: str):
        online_list = users_online.split(', ')
        online_list = filter(lambda u: u != self.client.username, online_list)
        self.user_list.set(list(online_list))

        # Default to First Item in ListBox
        self.user_listbox.select_set(0)  # This focus on the first item.
        self.user_listbox.event_generate("<<ListboxSelect>>")

    def _handle_message(self, author: str, message: str):
        chat_window = self.chat_windows.get(author)

        if chat_window is None:
            return

        chat_window.add_peer_message(message)

    def _handle_connect(self, peer_username: str):
        self.create_chat_window(peer_username)

    def _handle_disconnect(self, peer_username: str):
        self.destroy_chat_window(peer_username)

    def _on_refresh_list(self):
        self.client.request_list()

    def _on_start_chat(self):
        selection = self.user_listbox.curselection()

        if len(selection) == 0:
            return

        peer_username = self.user_listbox.get(selection[0])

        if peer_username in self.chat_windows.keys():
            messagebox.showerror('Error', f"You're already chatting with {peer_username}.")
            return

        self.create_chat_window(peer_username)
        self.client.connect_to_user(peer_username)

    def create_chat_window(self, peer_username: str):
        chat_window = ChatWindow(self, self.mainframe, peer_username)
        self.chat_windows[peer_username] = chat_window

    def destroy_chat_window(self, peer_username: str):
        chat_window = self.chat_windows.get(peer_username)

        if chat_window is None:
            return

        del self.chat_windows[peer_username]
        if chat_window.window.winfo_exists():
            chat_window.window.destroy()
