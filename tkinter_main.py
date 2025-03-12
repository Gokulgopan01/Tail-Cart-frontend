
import tkinter as tk
from portal.Proteck import PortalLogin
from tkinter_login import UserSelectionApp

if __name__ == "__main__":
    # Initialize the Tkinter root window
    root = tk.Tk()
    #client_data = {}  # Initialize client data

    # Create the PortalLogin instance
    #portal_login = PortalLogin(client_data)

    # Create the UI for client login
    ui = UserSelectionApp(root) 

    # Run the Tkinter mainloop
    root.mainloop()
