from tkinter import *

class Password_Generator:
    
    """
    simple app for generating a password
    """
    
    def __init__(self, parent: Tk):
        self.parent = parent
        self.password = Label(parent, text="", width=40)
        
        # output of password generator
        self.password.grid(column=1, row=2)
        self.password_label = Label(parent, text="Password", width=20) 
        self.password_label.grid(column=1, row=1)
        
        # label prompting the user what to do 
        self.prompt = Label(parent, text="Enter a password length between 1 and 30")
        self.prompt.grid(column=0, row=0)
        
        # input box for password length
        self.pwd_length_input = Entry(parent)
        self.pwd_length_input.grid(column=0, row=2)
        self.pwd_length_label = Label(parent, text="Password Length")
        self.pwd_length_label.grid(column=0, row=1)
        
        # interactive buttons for the user 
        
        # Generate Password button --> calls the generate() function and returns a string type 
        self.gen_pwd_button = Button(parent, text="Generate Password", command=self.generate)
        self.gen_pwd_button.grid(column=0, row=3)
        
        # Accept button --> closes the window and returns the password to the main program
        self.accept_button = Button(parent, text="Accept", command=self.accept)
        self.accept_button.grid(column=1, row=3)
        
        # Regenerate button --> calls the generate() function and returns a string type
        self.reGen_button = Button(parent, text="Regenerate", command=self.generate)
        self.reGen_button.grid(column=1, row=4)
        
    """
        generate password funcation 
    """
    def generate(self):
        import random
        import string
        
        # seeting the password length to be 40 characters or less 
        pwd_length = int(self.pwd_length_input.get())
        if pwd_length <= 40:
            pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=pwd_length))
            self.password.configure(text = str(pwd))
        
    """
        accept and quit funcation 
    """
    def accept(self):
        self.parent.destroy()
        self.parent.quit()
        
        
root = Tk()
app = Password_Generator(root)
root.mainloop()