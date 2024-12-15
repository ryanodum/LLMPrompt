import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pyperclip
import tiktoken

def num_tokens_from_string(string: str, encoding_name: str = "o200k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

class FileSelectorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File and Prompt Builder")

        root.geometry("1200x900")  # Set width to 1200px and height to 900px
        root.resizable(True, True)  # Allow resizing in both width and height

        # Directories for meta_prompts and instructions
        self.meta_prompts_dir = 'meta_prompts'
        self.instructions_dir = 'custom_instructions'

        # Frame for directory selection
        dir_frame = tk.Frame(self.master)
        dir_frame.pack(pady=5, fill=tk.X)

        self.select_dir_button = tk.Button(dir_frame, text="Select Directory (Text Files)", command=self.select_directory)
        self.select_dir_button.pack(side=tk.LEFT, padx=5)

        self.directory_label = tk.Label(dir_frame, text="No directory selected")
        self.directory_label.pack(side=tk.LEFT, padx=5, fill=tk.X)

        # Frame for the three listboxes
        lists_frame = tk.Frame(self.master)
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- C# (or any text) Files Listbox ---
        cs_frame = tk.Frame(lists_frame)
        cs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        cs_label = tk.Label(cs_frame, text="Select Files (any text-based):")
        cs_label.pack(anchor='w')

        cs_scroll = tk.Scrollbar(cs_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(cs_frame, selectmode=tk.EXTENDED, yscrollcommand=cs_scroll.set, exportselection=0)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cs_scroll.config(command=self.file_listbox.yview)
        cs_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        # --- Meta Prompts Listbox ---
        meta_frame = tk.Frame(lists_frame)
        meta_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        meta_label = tk.Label(meta_frame, text="Select Meta Prompts:")
        meta_label.pack(anchor='w')

        meta_scroll = tk.Scrollbar(meta_frame, orient=tk.VERTICAL)
        self.meta_listbox = tk.Listbox(meta_frame, selectmode=tk.EXTENDED, yscrollcommand=meta_scroll.set, exportselection=0)
        self.meta_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        meta_scroll.config(command=self.meta_listbox.yview)
        meta_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.meta_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        self.populate_listbox_from_dir(self.meta_listbox, self.meta_prompts_dir, ".txt")

        # --- Instructions Listbox ---
        instr_frame = tk.Frame(lists_frame)
        instr_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        instr_label = tk.Label(instr_frame, text="Select Instructions:")
        instr_label.pack(anchor='w')

        instr_scroll = tk.Scrollbar(instr_frame, orient=tk.VERTICAL)
        self.instr_listbox = tk.Listbox(instr_frame, selectmode=tk.EXTENDED, yscrollcommand=instr_scroll.set, exportselection=0)
        self.instr_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        instr_scroll.config(command=self.instr_listbox.yview)
        instr_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.instr_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        self.populate_listbox_from_dir(self.instr_listbox, self.instructions_dir, ".txt")

        # Frame for text input
        text_frame = tk.Frame(self.master)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_label = tk.Label(text_frame, text="Paste additional text here:")
        text_label.pack(anchor="w")

        self.text_input = tk.Text(text_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        self.text_input.bind("<KeyRelease>", lambda e: self.update_token_count())

        # Frame for action buttons
        action_frame = tk.Frame(self.master)
        action_frame.pack(pady=10)

        self.load_files_button = tk.Button(action_frame, text="Build and Copy Prompt", command=self.build_and_copy_prompt)
        self.load_files_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(action_frame, text="Exit", command=self.master.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Label to show token count dynamically
        self.token_count_label = tk.Label(self.master, text="Token count: 0")
        self.token_count_label.pack(pady=5)

        # Internal variable to store directory path for user-selected files
        self.selected_directory = None
        # Initial token count calculation
        self.update_token_count()

    def populate_listbox_from_dir(self, listbox, directory, extension):
        if os.path.isdir(directory):
            files = [f for f in os.listdir(directory) if f.endswith(extension)]
            for fname in files:
                listbox.insert(tk.END, fname)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory = directory
            self.directory_label.config(text=directory)
            self.populate_all_files(directory)
            self.update_token_count()

    def populate_all_files(self, directory):
        self.file_listbox.delete(0, tk.END)
        # Load all files, no filter
        files = os.listdir(directory)
        for filename in files:
            # We show all files. If it's binary or not readable, we'll skip later during reading.
            self.file_listbox.insert(tk.END, filename)

    def get_selected_files_text(self, directory, listbox):
        """Combine the text from selected files in the given listbox from directory."""
        selected_files = [listbox.get(i) for i in listbox.curselection()]
        if not directory:
            return ""

        combined = ''
        separator = '\n\n' + '#' * 25 + '\n\n'
        for f in selected_files:
            file_path = os.path.join(directory, f)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
                    if combined:
                        combined += separator
                    combined += file_content
                except (UnicodeDecodeError, PermissionError):
                    # If file can't be read as text, skip it quietly
                    pass
        return combined.strip()

    def get_current_prompt(self):
        # Get content from selected files in the chosen directory
        all_files_content = self.get_selected_files_text(self.selected_directory, self.file_listbox)
        if all_files_content:
            all_files_content = "### Contextual Prompt (from selected files) ###\n" + all_files_content

        # Get meta prompts content
        meta_content = self.get_selected_files_text(self.meta_prompts_dir, self.meta_listbox)

        # Get instructions content
        instructions_content = self.get_selected_files_text(self.instructions_dir, self.instr_listbox)
        if instructions_content:
            instructions_content = "### Instructions ###\n" + instructions_content

        # Get user text
        user_text = self.text_input.get("1.0", tk.END).strip()
        if user_text:
            user_text = "### Prompt and/or code to address ###\n" + user_text

        # Combine all parts
        parts = []
        if meta_content:
            parts.append(meta_content)
        if all_files_content:
            parts.append(all_files_content)
        if instructions_content:
            parts.append(instructions_content)
        if user_text:
            parts.append(user_text)

        full_prompt = "\n\n".join(parts).strip()
        return full_prompt

    def update_token_count(self):
        # Build current prompt
        current_prompt = self.get_current_prompt()
        # Count tokens
        token_count = num_tokens_from_string(current_prompt, "o200k_base")
        self.token_count_label.config(text=f"Token count: {token_count:,}")

    def build_and_copy_prompt(self):
        # If nothing selected and no text, warn
        if (not self.selected_directory
                and not self.meta_listbox.curselection()
                and not self.instr_listbox.curselection()
                and not self.text_input.get("1.0", tk.END).strip()):
            messagebox.showwarning("No input", "Please select files and/or choose meta prompts, instructions, or add text.")
            return

        full_prompt = self.get_current_prompt()
        token_count = num_tokens_from_string(full_prompt, "o200k_base")

        # Copy to clipboard
        pyperclip.copy(full_prompt)

        messagebox.showinfo("Prompt Built",
                            f"Your prompt has been built and copied to the clipboard.\nToken count: {token_count:,}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = FileSelectorGUI(root)
    root.mainloop()
