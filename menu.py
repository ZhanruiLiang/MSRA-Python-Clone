import Tkinter as tk

ItemW, ItemH = 400, 80
class Menu(tk.Frame):
    def __init__(self, parent, content):
        tk.Frame.__init__(self, parent)
        n = len(content)
        self.config(width=ItemW, height=ItemH*n)

        self.buttons = []
        for caption, callback in content:
            button = tk.Button(self, text=caption, command=callback)
            button.pack()
            self.buttons.append(button)
        self.buttons[0].focus()
