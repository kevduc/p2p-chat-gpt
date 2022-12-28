import threading
import socket
import tkinter as tk
import tkinter.simpledialog as simpledialog


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.username = "default"
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.receive_thread = threading.Thread(target=self.receive_messages)

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode("utf-8")
                if message == "NAMEREQUIRED":
                    self.client.send(f"{self.username}".encode("utf-8"))
                elif message == "NAMEEXISTS":
                    self.username = self.get_username()
                    self.client.send(f"{self.username}".encode("utf-8"))
                else:
                    self.messages_list.insert(tk.END, message)
            except OSError:  # Possibly client has left the chat.
                break

    def send_message(self, event=None):  # event is passed by binders.
        message = self.my_message.get()
        self.my_message.set("")  # Clears input field.
        self.client.send(f"{self.username}: {message}".encode("utf-8"))
        if message == "{quit}":
            self.client.close()
            self.top.quit()

    def get_username(self):
        username = simpledialog.askstring(
            "Username", "Enter a username:", parent=self.top)
        return username

    def on_closing(self, event=None):
        """This function is to be called when the window is closed."""
        self.my_message.set("{quit}")
        self.send_message()

    def start_chat(self):
        # Create the main window
        self.top = tk.Tk()
        self.top.title("Chatter")

        # Create the messages frame
        messages_frame = tk.Frame(self.top)
        self.my_message = tk.StringVar()  # For the messages to be sent.
        self.my_message.set("Type your messages here.")
        # To navigate through past messages.
        scrollbar = tk.Scrollbar(messages_frame)
        # Following will contain the messages.
        self.messages_list = tk.Listbox(
            messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.messages_list.pack()
        messages_frame.pack()

        # Create the entry field and the "Send" button
        entry_field = tk.Entry(self.top, textvariable=self.my_message)
        entry_field.bind("<Return>", self.send_message)
        entry_field.pack()
        send_button = tk.Button(self.top, text="Send",
                                command=self.send_message)
        send_button.pack()

        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.username = self.get_username()
        self.receive_thread.start()
        tk.mainloop()


if __name__ == "__main__":
    host = input("Enter host IP: ")
    port = int(input("Enter port: "))
    client = ChatClient(host, port)
    client.start_chat()
