import tkinter as tk

MAX_WIDTH = 800
MAX_HEIGHT = 200
REFRESH_RATE = 60


class ChatGUI(tk.Tk):
    def __init__(self, title, **kwargs):
        super().__init__()
        self.title(title)
        width = int(self.winfo_screenwidth() - 200)
        width = MAX_WIDTH if width > MAX_WIDTH else width
        height = int(self.winfo_screenheight() - 200)
        height = MAX_HEIGHT if height > MAX_HEIGHT else height
        self.geometry(f"{width}x{height}+100+100")
        self.text_content_array = []
        self.text_content = tk.StringVar()
        self.text_box = tk.Label(self, background="black", foreground="white", anchor=tk.NW, justify=tk.LEFT,
                                 textvariable=self.text_content)
        self.text_box.pack(fill=tk.BOTH, expand=True)
        self.text_box_scrollbar = tk.Scrollbar(self.text_box, command=self.text_box.yview)
        self.text_box_scrollbar.pack(side=tk.RIGHT)
        self.input_content = tk.StringVar()
        self.input_box = tk.Entry(self, textvariable=self.input_content)
        self.input_box.bind("<Return>", self.submit_message)
        self.input_box.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.refresh_screen()

    def refresh_screen(self):
        self.after(int(1000 / REFRESH_RATE), self.refresh_screen)

    def submit_message(self, event):
        input_content = self.input_content.get()
        self.text_content_array.append(input_content)
        self.input_content.set("")
        self.text_content.set("\n".join(self.text_content_array))


if __name__ == "__main__":
    window = ChatGUI(title="Test")
    window.text_content.set("BATATA")
    window.mainloop()
