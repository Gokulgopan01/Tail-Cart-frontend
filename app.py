import tkinter as tk
from screens.home_screen import HomeScreen
from screens.login_screen import LoginScreen
from tkinter import ttk

class Application(tk.Tk):
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Screen App")
        self.root.geometry("400x300")

        style = ttk.Style()
        style.theme_use('clam')

        self.container = ttk.Frame(root)
        self.container.pack(expand=True, fill='both')

        self.frames = {}

        for Screen in (LoginScreen, HomeScreen):
            frame = Screen(self.container, self)
            self.frames[Screen.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginScreen")

    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()