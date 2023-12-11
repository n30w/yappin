#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import re
import threading
import select
from tkinter import *
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from chat_utils import *
import json

import random
import string


# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""

    """ ====================== Login Window ====================== """

    def login(self):
        self.login = Toplevel()

        # set the prompt message for the user to enter name and password
        self.login.title("Login & Password")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)

        # create the prompt title and sets where the label will be placed in the window
        self.title = Label(
            self.login,
            text="Please login to continue",
            justify=CENTER,
            font="Helvetica 14 bold",
        )

        self.title.place(relheight=0.13, relx=0.2, rely=0.07)

        # create a NAME label and sets where it will be placed in the window
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")

        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

        # create a PASSWORD label and sets where it will be placed in the window
        self.labelPassword = Label(self.login, text="Password: ", font="Helvetica 12")

        self.labelPassword.place(relheight=0.2, relx=0.1, rely=0.35)

        # create a entry box for inputing username
        self.entryName = Entry(self.login, font="Helvetica 14")

        self.entryName.place(relwidth=0.5, relheight=0.12, relx=0.35, rely=0.2)

        # create an entry box for inputing the password
        self.entryPassword = Entry(self.login, font="Helvetica 14", show="*")

        self.entryPassword.place(relwidth=0.5, relheight=0.12, relx=0.35, rely=0.37)

        # set the focus of the curser
        # not really sure what this does lmao
        self.entryName.focus()

        # create a Continue Button to move onto the Chat window
        # BUT FIRST CHECKS the username and password with the .goAhead() funcation !!!!!
        self.go = Button(
            self.login,
            text="CONTINUE",
            font="Helvetica 14 bold",
            command=lambda: self.goAhead(
                self.entryName.get(), self.entryPassword.get()
            ),
        )

        self.go.place(relx=0.4, rely=0.55)
        self.Window.mainloop()

    def goAhead(self, name, password):
        # checks for strong password
        password_special_char = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
        password_num = re.compile("[0-9]")
        password_uppercase = re.compile("[A-Z]")

        # if eveything is satisfied then send the login-user to the server
        if (
            len(name) > 0
            and len(password) >= 10
            and password_special_char.search(password)
            and password_num.search(password)
            and password_uppercase.search(password)
        ):
            msg = json.dumps({"action": "login", "name": name, "password": password})
            self.send(msg)
            response = json.loads(self.recv())

            if response["status"] == "ok":
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                # while True:
                #     self.proc()

                # the thread to receive messages
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()

            elif response["status"] == "wrong password":
                messagebox.showerror("Error", "Incorrect password ")

            elif response["status"] == "duplicate":
                messagebox.showerror("Error", "Username already exists")

        # if password is not strong enough then suggest a stronger password
        elif (
            len(password) < 10
            or not password_special_char.search(password)
            or not password_num.search(password)
            or not password_uppercase.search(password)
        ):
            gen_password = "".join(
                random.choices(
                    string.ascii_letters + string.digits, k=random.randint(10, 30)
                )
            )
            messagebox.showerror(
                "Error",
                "Password must be at least 10 characters long, contain at least one special character, contain at least one number, and one uppercase letter. \n\n Suggested Password: "
                + gen_password,
            )

        # if username is not entered
        # room for imporvement: suggest a new username
        else:
            messagebox.showerror("Error", "Please fill all the fields")

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
        self.textCons.config(state=DISABLED)
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)

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
                self.system_msg += self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()


# create a GUI class object
if __name__ == "__main__":
    g = GUI()
