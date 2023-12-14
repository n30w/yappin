"""
Anything GUI related.
"""

import queue
import re

import threading
import select
from tkinter import *
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
import json

import ast

from client.client import Client


# GUI class for the chat
class GUI:
    # constructor method
    def __init__(
        self, gui_to_client_queue: queue.Queue, client_to_gui_queue: queue.Queue, client
    ) -> None:
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        self.__gui_to_client_queue: queue.Queue = gui_to_client_queue
        self.__client_to_gui_queue: queue.Queue = client_to_gui_queue

        self.__client = client

        self.my_msg = ""
        self.system_msg = ""

    """ +++++++++++++++++++ Login Window +++++++++++++++++++ """

    def login(self):
        self.login = Toplevel()

        # set the prompt message for the user to enter name and password
        self.login.title("Login & Password")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)

        """====================== Name ======================"""
        # create the prompt title and sets where the label will be placed in the window
        self.title = Label(
            self.login,
            text="Please login to continue",
            justify=CENTER,
            font="Helvetica 14 bold",
        )

        self.title.place(relheight=0.15, relx=0.2, rely=0.07)

        # create a NAME label and sets where it will be placed in the window
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")

        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

        # create a entry box for inputting username
        self.entryName = Entry(self.login, font="Helvetica 14")

        self.entryName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        # set the focus of the curser
        self.entryName.focus()

        """====================== Password ======================"""

        # create a PASSWORD label and sets where it will be placed in the window
        self.labelPassword = Label(self.login, text="Password: ", font="Helvetica 12")

        self.labelPassword.place(relheight=0.2, relx=0.1, rely=0.4)

        # create an entry box for inputting the password
        self.entryPassword = Entry(self.login, font="Helvetica 14", show="*")

        self.entryPassword.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.4)

        """====================== Signup ======================"""

        self.Signup = Button(
            self.login,
            text="Sign Up",
            font="Helvetica 14 bold",
            command=lambda: self.register(
                self.entryName.get(), self.entryPassword.get()
            ),
        )

        self.Signup.place(relx=0.4, rely=0.75)

        """====================== Login ======================"""
        self.Login = Button(
            self.login,
            text="Login",
            font="Helvetica 14 bold",
            command=lambda: self.goAhead(
                self.entryName.get(), self.entryPassword.get()
            ),
        )

        self.Login.place(relx=0.4, rely=0.55)

        """====================== Bindings ======================"""
        self.entryName.bind(
            "<Return>",
            lambda event: self.goAhead(self.entryName.get(), self.entryPassword.get()),
        )
        self.entryPassword.bind(
            "<Return>",
            lambda event: self.goAhead(self.entryName.get(), self.entryPassword.get()),
        )

        # Starts the mainloop!
        self.Window.mainloop()

    """ +++++++++++++++++++ To Server Side +++++++++++++++++++ """

    def goAhead(self, name, password):
        # if everything is satisfied, send the login-user to the server

        """====== Check if the user is already registered or not ======"""
        with open("userAccountBank.txt", "r") as f:
            accBank = ast.literal_eval(f.read())

        if name not in accBank.keys() or password not in accBank.values():
            messagebox.showerror(title="Login failed", message="Please sign up first.")
            return  # Don't execute the next part

        new_client = self.__client(name)

        client_thread = threading.Thread(target=new_client.run)
        client_thread.daemon = True
        client_thread.start()

        # msg = json.dumps({"action": "login", "name": name, "password": password})
        # self.send(msg)
        # print(msg)

        # response = json.loads(self.recv())

        self.login.destroy()

        self.layout(name)

        self.textCons.config(state=NORMAL)
        # self.textCons.insert(END, "hello" +"\n\n")
        self.textCons.insert(END, menu + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        # if response["status"] == "success":
        #     self.login.destroy()
        #     self.sm.set_state(S_LOGGEDIN)
        #     self.sm.set_myname(name)

        # while True:
        #     self.proc()

        # elif response["status"] == "wrong password":
        #     messagebox.showerror("Error", "Incorrect password")
        #     return

        # elif response["status"] == "duplicate":
        #     messagebox.showerror("Error", "duplicate username")
        #     return

        # # the thread to receive messages
        # process = threading.Thread(target=self.proc)
        # process.daemon = True
        # process.start()

    """ +++++++++++++++++++ Register New Users +++++++++++++++++++ """

    def register(self, name, password):
        # checks for strong password
        password_special_char = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
        password_num = re.compile("[0-9]")
        password_uppercase = re.compile("[A-Z]")

        if (
            len(name) > 0
            and len(password) >= 10
            and password_special_char.search(password)
            and password_num.search(password)
            and password_uppercase.search(password)
        ):
            # Read existing content from the file
            try:
                with open("userAccountBank.txt", "r") as f:
                    accBank = ast.literal_eval(f.read())
            except FileNotFoundError:
                accBank = {}

            # Don't allow duplicate usernames or passwords
            if name in accBank.keys() or password in accBank.values():
                messagebox.showerror(
                    title="Login failed",
                    message="Username or Password is already in use.",
                )
                return  # Don't execute the next part

            # If not caught by the above check, execute below
            with open("userAccountBank.txt", "w") as f:
                # Store name: password pair into the password bank txt file for later use
                accBank[name] = password
                f.write(str(accBank))

            # Display a success message
            messagebox.showinfo(
                title="You have successfully signed up",
                message="Click 'Log in' to enter the chat room!",
            )

    """ +++++++++++++++++++ Chat Window +++++++++++++++++++"""

    # The main layout of the chat
    def layout(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")

        self.labelHead = Label(
            self.Window,
            bg="#17202A",
            fg="#EAECEE",
            text=self.name,
            font="Helvetica 13 bold",
            pady=5,
        )
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.textCons = Text(
            self.Window,
            width=20,
            height=2,
            bg="#17202A",
            fg="#EAECEE",
            font="Helvetica 14",
            padx=5,
            pady=5,
        )
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        self.entryMsg = Entry(
            self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13"
        )

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.entryMsg.focus()
        self.entryMsg.bind(
            "<Return>", lambda event: self.sendButton(self.entryMsg.get())
        )

        # create a Send Button
        self.buttonMsg = Button(
            self.labelBottom,
            text="Send",
            font="Helvetica 10 bold",
            width=20,
            bg="#ABB2B9",
            command=lambda: self.sendButton(self.entryMsg.get()),
        )

        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, msg + "\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()
