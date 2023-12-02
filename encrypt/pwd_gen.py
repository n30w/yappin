from tkinter import *

from client.encryption import generate_password

# Constants defining minimum and maximum character count for password
MIN_CHAR: int = 5
MAX_CHAR: int = 40


class GUI_Password_Generator:
    """
    Constructs a GUI for password generation function from encryption. Returns result back to main chat program.
    """

    def __init__(self, parent: Tk) -> None:
        self.parent = parent

        """
        GUI Components
        """
        self.password = Label(parent, text="", width=40)

        # Output of password generator
        self.password_label = Label(parent, text="Password", width=20)

        # User prompt label
        self.prompt = Label(
            parent,
            text=(f"Choose a length between {MIN_CHAR} to {MAX_CHAR} characters"),
        )

        # Slider for password length
        self.slider = Scale(parent, from_=MIN_CHAR, to=MAX_CHAR, orient=HORIZONTAL)
        self.slider.set(MIN_CHAR)

        # Generate Password button --> calls the generate() function and returns a string type
        self.gen_button = Button(
            parent, text="Generate Password", command=self.display_generated_password
        )

        # Regenerate button --> calls the generate() function and returns a string type
        self.reGen_button = Button(
            parent, text="Regenerate", command=self.display_generated_password
        )

        # Accept button --> closes the window and returns the password to the main program
        self.accept_button = Button(
            parent, text="Accept", command=self.destroy_and_quit
        )

        """
        GUI Layout
        """

        # Informational
        self.password.grid(column=1, row=2)
        self.password_label.grid(column=1, row=1)
        self.prompt.grid(column=0, row=0)

        # Interactive
        self.slider.grid(column=0, row=1)
        self.gen_button.grid(column=0, row=3)
        self.reGen_button.grid(column=1, row=4)
        self.accept_button.grid(column=1, row=3)

    def display_generated_password(self) -> None:
        """Button callback, updates password text."""
        password: str = generate_password(self.slider.get())
        self.password.configure(text=password)

    def destroy_and_quit(self) -> None:
        """Destroys and quits the GUI."""
        self.parent.destroy()
        self.parent.quit()


root = Tk()
app = GUI_Password_Generator(root)
root.mainloop()
