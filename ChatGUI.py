import re
import tkinter as tk

MAX_WIDTH = 800
MAX_HEIGHT = 800
REFRESH_RATE = 60


class ChatGUI(tk.Tk):
    def __init__(self, title, socket, **kwargs):
        super().__init__()
        self.title(title)
        self.socket = socket
        self.protocol("WM_DELETE_WINDOW", self.close_connection)
        width = int(self.winfo_screenwidth() - 200)
        width = MAX_WIDTH if width > MAX_WIDTH else width
        height = int(self.winfo_screenheight() - 200)
        height = MAX_HEIGHT if height > MAX_HEIGHT else height
        self.geometry(f"{width}x{height}+100+100")
        # Data
        self.text_content_array = []
        self.input_content = tk.StringVar()
        # Init Input Box
        self.input_box = tk.Entry(self, textvariable=self.input_content)
        self.input_box.bind("<Return>", self.submit_message)
        self.input_box.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.input_box.focus_set()
        self.bind("<1>", lambda x: self.input_box.focus_set())
        # Init Text Box
        self.text_box_frame = tk.Frame(self)
        self.text_box_frame.pack(fill=tk.BOTH, expand=True)
        self.text_box_frame.pack_propagate(False)
        self.text_box = tk.Text(self.text_box_frame, background="black", foreground="white", state=tk.NORMAL)
        self.text_box.delete("0.0", tk.END)
        self.scrollbar = tk.Scrollbar(self.text_box_frame, command=self.text_box.yview, orient=tk.VERTICAL)
        self.text_box['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def add_message(self, message):
        text_box_content = self.text_box.get("0.0", tk.END)
        new_line = "\n" if text_box_content != "\n" else ""
        added_line = new_line + message
        self.text_box.insert(tk.END, added_line)
        self.text_box.see(tk.END)

    def submit_message(self, _):
        input_content = self.input_content.get()
        self.input_content.set("")
        self.add_message("> " + input_content)
        self.socket.send(input_content.encode())
        if re.match(r"^/exit\s", input_content):
            self.destroy()

    def close_connection(self):
        self.socket.send("/exit".encode())
        self.destroy()
