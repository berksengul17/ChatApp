import threading
import tkinter as tk
import pygame, socket
from tkinter import messagebox

users = {"jack": "123",
         "carl": "1234",
         "carol": "12345"}

HEADER = 10
IP = "127.0.0.1"
PORT = 1234
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

class App:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("300x150")
        self.root.resizable(False, False)


        self.entry_username = tk.Entry(self.root)
        self.username = self.entry_username.get()
        self.entry_username.focus()

        self.entry_password = tk.Entry(self.root, show="*")

        self.entry_ip = tk.Entry(self.root)
        self.entry_ip.insert(0, "127.0.0.1")

        self.lbl_username = tk.Label(self.root, text="Username:")
        self.lbl_password = tk.Label(self.root, text="Password:")
        self.lbl_ip = tk.Label(self.root, text="Ip:")

        self.btn_login = tk.Button(self.root, text="Login", command=self.login)

        self.lbl_username.place(relx = 0.18, rely = 0.3, anchor = tk.CENTER)
        self.lbl_password.place(relx = 0.18, rely = 0.45, anchor = tk.CENTER)
        self.lbl_ip.place(relx = 0.18, rely = 0.6, anchor = tk.CENTER)

        self.entry_username.place(relx = 0.5, rely = 0.3, anchor = tk.CENTER)
        self.entry_password.place(relx = 0.5, rely = 0.45, anchor = tk.CENTER)
        self.entry_ip.place(relx = 0.5, rely = 0.6, anchor = tk.CENTER)

        self.btn_login.place(relx = 0.5, rely = 0.8, anchor = tk.CENTER)

        self.root.bind("<Return>", self.login)

        self.root.mainloop()

    def login(self, *args):
        for username, password in users.items():
            if self.entry_username.get() == username and self.entry_password.get() == password:
                self.root.withdraw()
                self.connect()
                self.openChat()
                break
        else:
            self.play_sound()
            messagebox.showinfo("Warning!", "Wrong Credentials!")

    def play_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("wrongCredentialsSound.mp3")
        pygame.mixer.music.play()

    def connect(self):
        self.send_username()
        rcv = threading.Thread(target=self.receive_message)
        rcv.start()

    def openChat(self):
        self.window = tk.Toplevel()
        self.window.title("ZORT CHAT")
        self.window.geometry("500x500")
        self.window.deiconify()
        self.window.resizable(False, False)

        self.chatFrame = tk.Frame(self.window, width=500, height=400, bg="red")
        self.chatFrame.pack_propagate(False)
        self.chatFrame.pack(fill=tk.BOTH, expand=1)

        self.chatLog = tk.Text(self.chatFrame, width=400, height=400, padx=5, pady=5)
        self.chatLog.pack_propagate(False)
        self.chatLog.pack(fill=tk.BOTH, expand=1)
        self.chatLog.configure(state=tk.DISABLED, cursor="arrow")

        self.scrollbar = tk.Scrollbar(self.chatLog)
        self.scrollbar.pack_propagate(False)
        self.scrollbar.pack(side=tk.RIGHT, fil=tk.Y)
        self.scrollbar.config(command=self.chatLog.yview)

        self.msgFrame = tk.Frame(self.window, width=500, height=100, bg="yellow")
        self.msgFrame.pack_propagate(False)
        self.msgFrame.pack()

        self.msg_box = tk.Text(self.msgFrame, width=50, height=6, padx=5, pady=5, wrap=tk.CHAR)
        self.msg_box.pack_propagate(False)
        self.msg_box.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.msg_box.focus()

        self.btn_send = tk.Button(self.msgFrame, width=10, height=6, text="Send", padx=5, pady=5,
                                  bg="blue", command=lambda: self.send_button(self.msg_box.get("1.0", tk.END)))
        self.btn_send.pack_propagate(False)
        self.btn_send.pack(side=tk.LEFT, fill=tk.X, expand=1)


        self.window.mainloop()

    def send_button(self, msg):
        self.msg = msg
        print(self.msg)
        self.msg_box.delete("1.0", tk.END)
        send = threading.Thread(target=self.send_message)
        send.start()


    def send_message(self):
        msg = self.msg.encode(FORMAT)
        msg_header = f"{len(msg) :< {HEADER}}".encode(FORMAT)
        client_socket.send(msg_header + msg)

    def send_username(self):
        username = self.entry_username.get().encode(FORMAT)
        username_header = f"{len(username) :< {HEADER}}".encode(FORMAT)
        client_socket.send(username_header + username)


    def receive_message(self):
        while True:
            try:
                username_header = client_socket.recv(HEADER).decode(FORMAT)
                if not username_header:
                    print(f"Connection closed on server")

                username = client_socket.recv(int(username_header)).decode(FORMAT)

                msg_header = client_socket.recv(HEADER).decode(FORMAT)
                msg_len = int(msg_header)
                msg = client_socket.recv(msg_len).decode(FORMAT)

                self.chatLog.configure(state = tk.NORMAL)
                self.chatLog.insert(tk.END, f"{username}: {msg}")
                self.chatLog.configure(state = tk.DISABLED)
                self.chatLog.see(tk.END)

            except Exception as e:
                print("ERROR", e)
                client_socket.close()
                break


app = App()
