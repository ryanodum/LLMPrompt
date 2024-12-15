import tkinter as tk
from tkinter import filedialog, messagebox
import os

class FileSelectorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File Selector")

        # Frame for directory selection
        dir_frame = tk.Frame(self.master)
        dir_frame.pack(pady=5)

        self.select_dir_button = tk.Button(dir_frame, text="Select Directory", command=self.select_directory)
        self.select_dir_button.pack(side=tk.LEFT, padx=5)

        self.directory_label = tk.Label(dir_frame, text="No directory selected")
        self.directory_label.pack(side=tk.LEFT, padx=5)

        # Frame for file list
        self.list_frame = tk.Frame(self.master)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar for the file listbox
        self.scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(self.list_frame, selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)

        # Frame for text input
        text_frame = tk.Frame(self.master)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_label = tk.Label(text_frame, text="Paste additional text here:")
        text_label.pack(anchor="w")

        self.text_input = tk.Text(text_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # Frame for action buttons
        action_frame = tk.Frame(self.master)
        action_frame.pack(pady=10)

        self.load_files_button = tk.Button(action_frame, text="Load Selected Files", command=self.load_selected_files)
        self.load_files_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(action_frame, text="Exit", command=self.master.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Internal variable to store directory path
        self.selected_directory = None

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory = directory
            self.directory_label.config(text=directory)
            self.populate_file_listbox(directory)

    def populate_file_listbox(self, directory):
        self.file_listbox.delete(0, tk.END)
        # Adjust the file pattern as needed, e.g., ".cs"
        for filename in os.listdir(directory):
            if filename.endswith(".cs"):
                self.file_listbox.insert(tk.END, filename)

    def load_selected_files(self):
        if not self.selected_directory:
            messagebox.showwarning("No directory selected", "Please select a directory first.")
            return

        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        if not selected_files:
            messagebox.showwarning("No files selected", "Please select one or more files.")
            return

        # Get the user-pasted text
        user_text = self.text_input.get("1.0", tk.END).strip()

        # Here you have selected_files and user_text that can be passed to your existing logic
        # For instance, you can write them to a temporary file or directly pass them to your DirExporter or Main logic.

        # Example: Print them out for now
        print("Selected files:")
        for f in selected_files:
            print(f)
        print("\nUser Text:")
        print(user_text)

        # You could also directly call the functions from DirExporter or incorporate this GUI in Main.
        # Or save these selections to a known location that Main.py can read.

        messagebox.showinfo("Files Loaded", "Your selected files and text have been loaded.\nYou can now run your main program logic.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = FileSelectorGUI(root)
    root.mainloop()
