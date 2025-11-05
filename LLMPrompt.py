import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import pyperclip
import tiktoken
import xml.sax.saxutils as saxutils


def num_tokens_from_string(string: str, encoding_name: str = "o200k_base") -> int:
    """Calculate the number of tokens in a string using tiktoken."""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))


class FileSelectorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File and Prompt Builder")

        self.master.geometry("1400x950")  # Increased size for preview pane
        self.master.resizable(True, True)

        # Directories for meta_prompts and instructions
        self.meta_prompts_dir = 'meta_prompts'
        self.instructions_dir = 'custom_instructions'
        self.config_file = 'llmprompt_config.json'
        self.recent_dirs_file = 'recent_directories.json'

        # Internal variable to store directory path for user-selected files
        self.selected_directory = None
        self.all_files = []  # Store all files for filtering

        # Load recent directories
        self.recent_directories = self.load_recent_directories()

        # Setup menu bar
        self.create_menu_bar()

        # Frame for directory selection
        dir_frame = tk.Frame(self.master)
        dir_frame.pack(pady=5, fill=tk.X)

        self.select_dir_button = tk.Button(
            dir_frame, text="Select Directory (Text Files)",
            command=self.select_directory
        )
        self.select_dir_button.pack(side=tk.LEFT, padx=5)

        # Recent directories dropdown
        self.recent_var = tk.StringVar()
        self.recent_dropdown = ttk.Combobox(
            dir_frame, textvariable=self.recent_var,
            values=self.recent_directories, width=50, state="readonly"
        )
        self.recent_dropdown.pack(side=tk.LEFT, padx=5)
        self.recent_dropdown.bind("<<ComboboxSelected>>", self.on_recent_selected)

        self.directory_label = tk.Label(dir_frame, text="No directory selected")
        self.directory_label.pack(side=tk.LEFT, padx=5, fill=tk.X)

        # Search frame for file filtering
        search_frame = tk.Frame(self.master)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Filter Files:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)

        clear_search_btn = tk.Button(
            search_frame, text="Clear Filter",
            command=lambda: self.search_var.set("")
        )
        clear_search_btn.pack(side=tk.LEFT, padx=5)

        # Main content area with paned window for resizable sections
        main_paned = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: listboxes
        left_frame = tk.Frame(main_paned)
        main_paned.add(left_frame, minsize=600)

        # Frame for the three listboxes
        lists_frame = tk.Frame(left_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # --- Files Listbox (filtered for UTF-8 readable text) ---
        cs_frame = tk.Frame(lists_frame)
        cs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        cs_header_frame = tk.Frame(cs_frame)
        cs_header_frame.pack(fill=tk.X)

        cs_label = tk.Label(cs_header_frame, text="Select Files (text-based only):")
        cs_label.pack(side=tk.LEFT, anchor='w')

        self.file_count_label = tk.Label(cs_header_frame, text="(0/0)")
        self.file_count_label.pack(side=tk.RIGHT, anchor='e')

        cs_scroll = tk.Scrollbar(cs_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(
            cs_frame, selectmode=tk.EXTENDED,
            yscrollcommand=cs_scroll.set, exportselection=0
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cs_scroll.config(command=self.file_listbox.yview)
        cs_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        # Control buttons for files
        cs_btn_frame = tk.Frame(cs_frame)
        cs_btn_frame.pack(fill=tk.X, pady=2)

        tk.Button(
            cs_btn_frame, text="Select All",
            command=lambda: self.select_all_listbox(self.file_listbox)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            cs_btn_frame, text="Deselect All",
            command=lambda: self.deselect_all_listbox(self.file_listbox)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            cs_btn_frame, text="Clear",
            command=self.clear_files
        ).pack(side=tk.LEFT, padx=2)

        # --- Meta Prompts Listbox ---
        meta_frame = tk.Frame(lists_frame)
        meta_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        meta_header_frame = tk.Frame(meta_frame)
        meta_header_frame.pack(fill=tk.X)

        meta_label = tk.Label(meta_header_frame, text="Select Meta Prompts:")
        meta_label.pack(side=tk.LEFT, anchor='w')

        self.meta_count_label = tk.Label(meta_header_frame, text="(0/0)")
        self.meta_count_label.pack(side=tk.RIGHT, anchor='e')

        meta_scroll = tk.Scrollbar(meta_frame, orient=tk.VERTICAL)
        self.meta_listbox = tk.Listbox(
            meta_frame, selectmode=tk.EXTENDED,
            yscrollcommand=meta_scroll.set, exportselection=0
        )
        self.meta_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        meta_scroll.config(command=self.meta_listbox.yview)
        meta_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.meta_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        self.populate_listbox_from_dir(self.meta_listbox, self.meta_prompts_dir, ".txt")

        # Control buttons for meta prompts
        meta_btn_frame = tk.Frame(meta_frame)
        meta_btn_frame.pack(fill=tk.X, pady=2)

        tk.Button(
            meta_btn_frame, text="Select All",
            command=lambda: self.select_all_listbox(self.meta_listbox)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            meta_btn_frame, text="Deselect All",
            command=lambda: self.deselect_all_listbox(self.meta_listbox)
        ).pack(side=tk.LEFT, padx=2)

        # --- Instructions Listbox ---
        instr_frame = tk.Frame(lists_frame)
        instr_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        instr_header_frame = tk.Frame(instr_frame)
        instr_header_frame.pack(fill=tk.X)

        instr_label = tk.Label(instr_header_frame, text="Select Instructions:")
        instr_label.pack(side=tk.LEFT, anchor='w')

        self.instr_count_label = tk.Label(instr_header_frame, text="(0/0)")
        self.instr_count_label.pack(side=tk.RIGHT, anchor='e')

        instr_scroll = tk.Scrollbar(instr_frame, orient=tk.VERTICAL)
        self.instr_listbox = tk.Listbox(
            instr_frame, selectmode=tk.EXTENDED,
            yscrollcommand=instr_scroll.set, exportselection=0
        )
        self.instr_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        instr_scroll.config(command=self.instr_listbox.yview)
        instr_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.instr_listbox.bind("<<ListboxSelect>>", lambda e: self.update_token_count())

        self.populate_listbox_from_dir(self.instr_listbox, self.instructions_dir, ".txt")

        # Control buttons for instructions
        instr_btn_frame = tk.Frame(instr_frame)
        instr_btn_frame.pack(fill=tk.X, pady=2)

        tk.Button(
            instr_btn_frame, text="Select All",
            command=lambda: self.select_all_listbox(self.instr_listbox)
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            instr_btn_frame, text="Deselect All",
            command=lambda: self.deselect_all_listbox(self.instr_listbox)
        ).pack(side=tk.LEFT, padx=2)

        # Frame for text input
        text_frame = tk.Frame(left_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_header_frame = tk.Frame(text_frame)
        text_header_frame.pack(fill=tk.X)

        text_label = tk.Label(
            text_header_frame,
            text="Add your prompt, or paste additional text here:"
        )
        text_label.pack(side=tk.LEFT, anchor="w")

        tk.Button(
            text_header_frame, text="Clear Text",
            command=self.clear_text_input
        ).pack(side=tk.RIGHT, padx=2)

        self.text_input = tk.Text(text_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        self.text_input.bind("<KeyRelease>", lambda e: self.update_token_count())

        # Right side: preview pane
        preview_frame = tk.Frame(main_paned)
        main_paned.add(preview_frame, minsize=400)

        preview_label = tk.Label(preview_frame, text="Prompt Preview:", font=('TkDefaultFont', 10, 'bold'))
        preview_label.pack(anchor='w', padx=5, pady=5)

        preview_scroll = tk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        self.preview_text = tk.Text(
            preview_frame, wrap=tk.WORD,
            yscrollcommand=preview_scroll.set,
            state=tk.DISABLED, bg='#f5f5f5'
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview_text.yview)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame for action buttons
        action_frame = tk.Frame(self.master)
        action_frame.pack(pady=10)

        self.build_button = tk.Button(
            action_frame, text="Build and Copy Prompt (Ctrl+B)",
            command=self.build_and_copy_prompt, font=('TkDefaultFont', 10, 'bold')
        )
        self.build_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(
            action_frame, text="Export to File (Ctrl+E)",
            command=self.export_to_file
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = tk.Button(
            action_frame, text="Refresh Preview (Ctrl+R)",
            command=self.refresh_preview
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(action_frame, text="Exit", command=self.master.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Label to show token count dynamically
        self.token_count_label = tk.Label(
            self.master, text="Token count: 0",
            font=('TkDefaultFont', 10, 'bold')
        )
        self.token_count_label.pack(pady=5)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initial updates
        self.update_all_counts()
        self.update_token_count()

    def create_menu_bar(self):
        """Create menu bar with File menu."""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(
            label="Save Configuration (Ctrl+S)",
            command=self.save_configuration
        )
        file_menu.add_command(
            label="Load Configuration (Ctrl+O)",
            command=self.load_configuration
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Export Prompt to File (Ctrl+E)",
            command=self.export_to_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.master.bind('<Control-b>', lambda e: self.build_and_copy_prompt())
        self.master.bind('<Control-B>', lambda e: self.build_and_copy_prompt())
        self.master.bind('<Control-s>', lambda e: self.save_configuration())
        self.master.bind('<Control-S>', lambda e: self.save_configuration())
        self.master.bind('<Control-o>', lambda e: self.load_configuration())
        self.master.bind('<Control-O>', lambda e: self.load_configuration())
        self.master.bind('<Control-r>', lambda e: self.refresh_preview())
        self.master.bind('<Control-R>', lambda e: self.refresh_preview())
        self.master.bind('<Control-e>', lambda e: self.export_to_file())
        self.master.bind('<Control-E>', lambda e: self.export_to_file())

    def show_shortcuts(self):
        """Display keyboard shortcuts dialog."""
        shortcuts = """
Keyboard Shortcuts:

Ctrl+B - Build and Copy Prompt
Ctrl+S - Save Configuration
Ctrl+O - Load Configuration
Ctrl+R - Refresh Preview
Ctrl+E - Export to File
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def show_about(self):
        """Display about dialog."""
        about_text = """
LLM Prompt Builder
Version 2.0

A tool for building structured prompts for Large Language Models.

Features:
- Multi-file selection and combination
- Meta-prompts and instructions
- Real-time token counting
- Save/Load configurations
- Preview pane
- Search and filter
- Keyboard shortcuts
"""
        messagebox.showinfo("About", about_text)

    def load_recent_directories(self):
        """Load recent directories from file."""
        try:
            if os.path.exists(self.recent_dirs_file):
                with open(self.recent_dirs_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading recent directories: {e}")
        return []

    def save_recent_directories(self):
        """Save recent directories to file."""
        try:
            with open(self.recent_dirs_file, 'w') as f:
                json.dump(self.recent_directories, f, indent=2)
        except Exception as e:
            print(f"Error saving recent directories: {e}")

    def add_recent_directory(self, directory):
        """Add a directory to recent directories list."""
        if directory in self.recent_directories:
            self.recent_directories.remove(directory)
        self.recent_directories.insert(0, directory)
        self.recent_directories = self.recent_directories[:10]  # Keep only 10 most recent
        self.recent_dropdown['values'] = self.recent_directories
        self.save_recent_directories()

    def on_recent_selected(self, event):
        """Handle recent directory selection."""
        selected = self.recent_var.get()
        if selected and os.path.isdir(selected):
            self.selected_directory = selected
            self.directory_label.config(text=selected)
            self.populate_text_files(selected)
            self.update_token_count()

    def populate_listbox_from_dir(self, listbox, directory, extension):
        """Populate a listbox with files from a directory."""
        if os.path.isdir(directory):
            try:
                files = sorted([f for f in os.listdir(directory) if f.endswith(extension)])
                for fname in files:
                    listbox.insert(tk.END, fname)
            except Exception as e:
                print(f"Error populating listbox from {directory}: {e}")

    def select_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory = directory
            self.directory_label.config(text=directory)
            self.add_recent_directory(directory)
            self.populate_text_files(directory)
            self.update_token_count()

    def can_read_as_utf8(self, file_path, chunk_size=8192):
        """Check if a file can be read as UTF-8 text."""
        if not os.path.isfile(file_path):
            return False
        try:
            with open(file_path, 'rb') as f:
                data = f.read(chunk_size)
            data.decode('utf-8')
            return True
        except (UnicodeDecodeError, PermissionError, Exception):
            return False

    def populate_text_files(self, directory):
        """Populate the files listbox with UTF-8 readable files."""
        self.file_listbox.delete(0, tk.END)
        self.all_files = []
        try:
            files = sorted(os.listdir(directory))
            for filename in files:
                file_path = os.path.join(directory, filename)
                if self.can_read_as_utf8(file_path):
                    self.all_files.append(filename)
                    self.file_listbox.insert(tk.END, filename)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading directory: {e}")
        self.update_all_counts()

    def filter_files(self, *args):
        """Filter files based on search term."""
        if not self.selected_directory:
            return

        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)

        for filename in self.all_files:
            if search_term in filename.lower():
                self.file_listbox.insert(tk.END, filename)

        self.update_all_counts()

    def select_all_listbox(self, listbox):
        """Select all items in a listbox."""
        listbox.select_set(0, tk.END)
        self.update_token_count()

    def deselect_all_listbox(self, listbox):
        """Deselect all items in a listbox."""
        listbox.selection_clear(0, tk.END)
        self.update_token_count()

    def clear_files(self):
        """Clear file selection and directory."""
        self.selected_directory = None
        self.directory_label.config(text="No directory selected")
        self.file_listbox.delete(0, tk.END)
        self.all_files = []
        self.search_var.set("")
        self.update_token_count()

    def clear_text_input(self):
        """Clear the text input area."""
        self.text_input.delete("1.0", tk.END)
        self.update_token_count()

    def update_all_counts(self):
        """Update all count labels."""
        file_total = self.file_listbox.size()
        file_selected = len(self.file_listbox.curselection())
        self.file_count_label.config(text=f"({file_selected}/{file_total})")

        meta_total = self.meta_listbox.size()
        meta_selected = len(self.meta_listbox.curselection())
        self.meta_count_label.config(text=f"({meta_selected}/{meta_total})")

        instr_total = self.instr_listbox.size()
        instr_selected = len(self.instr_listbox.curselection())
        self.instr_count_label.config(text=f"({instr_selected}/{instr_total})")

    def get_selected_files_text(self, directory, listbox):
        """Combine the text from selected files in the given listbox from directory."""
        selected_files = [listbox.get(i) for i in listbox.curselection()]
        if not directory:
            return ""

        combined = ''
        separator = '\n\n' + '#' * 25 + '\n\n'
        for f in selected_files:
            file_path = os.path.join(directory, f)
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        file_content = file.read()
                    if combined:
                        combined += separator
                    sanitized_filename = saxutils.escape(f)
                    combined += f"<{sanitized_filename}>\n{file_content}\n</{sanitized_filename}>"
            except Exception as e:
                print(f"Error reading file {f}: {e}")
                combined += f"\n[Error reading file: {f}]\n"

        return combined.strip()

    def get_current_prompt(self):
        """Build and return the current prompt."""
        # Get content from selected text files in the chosen directory
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
            user_text = "### Direct Prompt from User and/or code to address ###\n" + user_text

        # Combine all parts
        parts = []
        parts.append("<FullPrompt>")
        if meta_content:
            parts.append("<MetaPrompt>")
            parts.append(meta_content)
            parts.append("</MetaPrompt>")
        if all_files_content:
            parts.append("<ContextualPrompt>")
            parts.append(all_files_content)
            parts.append("</ContextualPrompt>")
        if instructions_content:
            parts.append("<Instructions>")
            parts.append(instructions_content)
            parts.append("</Instructions>")
        if user_text:
            parts.append("<DirectPrompt>")
            parts.append(user_text)
            parts.append("</DirectPrompt>")
        parts.append("</FullPrompt>")

        full_prompt = "\n\n".join(parts).strip()
        return full_prompt

    def update_token_count(self):
        """Update token count and preview."""
        self.update_all_counts()

        # Build current prompt
        current_prompt = self.get_current_prompt()

        # Count tokens
        try:
            token_count = num_tokens_from_string(current_prompt, "o200k_base")
            self.token_count_label.config(text=f"Token count: {token_count:,}")
        except Exception as e:
            self.token_count_label.config(text=f"Token count: Error ({e})")

        # Update preview
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", current_prompt)
        self.preview_text.config(state=tk.DISABLED)

    def refresh_preview(self):
        """Manually refresh the preview."""
        self.update_token_count()

    def build_and_copy_prompt(self):
        """Build the prompt and copy to clipboard."""
        # If nothing selected and no text, warn
        if (not self.selected_directory
                and not self.meta_listbox.curselection()
                and not self.instr_listbox.curselection()
                and not self.text_input.get("1.0", tk.END).strip()):
            messagebox.showwarning(
                "No input",
                "Please select files and/or choose meta prompts, instructions, or add text."
            )
            return

        try:
            full_prompt = self.get_current_prompt()
            token_count = num_tokens_from_string(full_prompt, "o200k_base")

            # Copy to clipboard
            pyperclip.copy(full_prompt)

            messagebox.showinfo(
                "Prompt Built",
                f"Your prompt has been built and copied to the clipboard.\nToken count: {token_count:,}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error building prompt: {e}")

    def export_to_file(self):
        """Export the built prompt to a text file."""
        full_prompt = self.get_current_prompt()
        if not full_prompt or full_prompt == "<FullPrompt>\n\n</FullPrompt>":
            messagebox.showwarning("No Content", "Nothing to export. Please build a prompt first.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="prompt.txt"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_prompt)

                token_count = num_tokens_from_string(full_prompt, "o200k_base")
                messagebox.showinfo(
                    "Export Successful",
                    f"Prompt exported to:\n{file_path}\n\nToken count: {token_count:,}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting prompt: {e}")

    def save_configuration(self):
        """Save current configuration to a JSON file."""
        try:
            config = {
                'selected_directory': self.selected_directory,
                'selected_files': [self.file_listbox.get(i) for i in self.file_listbox.curselection()],
                'selected_meta': [self.meta_listbox.get(i) for i in self.meta_listbox.curselection()],
                'selected_instructions': [self.instr_listbox.get(i) for i in self.instr_listbox.curselection()],
                'user_text': self.text_input.get("1.0", tk.END).strip()
            }

            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="llmprompt_config.json"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", f"Configuration saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving configuration: {e}")

    def load_configuration(self):
        """Load configuration from a JSON file."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Load directory
                if config.get('selected_directory') and os.path.isdir(config['selected_directory']):
                    self.selected_directory = config['selected_directory']
                    self.directory_label.config(text=self.selected_directory)
                    self.populate_text_files(self.selected_directory)
                    self.add_recent_directory(self.selected_directory)

                # Select files
                if 'selected_files' in config:
                    for i in range(self.file_listbox.size()):
                        if self.file_listbox.get(i) in config['selected_files']:
                            self.file_listbox.select_set(i)

                # Select meta prompts
                if 'selected_meta' in config:
                    for i in range(self.meta_listbox.size()):
                        if self.meta_listbox.get(i) in config['selected_meta']:
                            self.meta_listbox.select_set(i)

                # Select instructions
                if 'selected_instructions' in config:
                    for i in range(self.instr_listbox.size()):
                        if self.instr_listbox.get(i) in config['selected_instructions']:
                            self.instr_listbox.select_set(i)

                # Load user text
                if 'user_text' in config:
                    self.text_input.delete("1.0", tk.END)
                    self.text_input.insert("1.0", config['user_text'])

                self.update_token_count()
                messagebox.showinfo("Success", "Configuration loaded successfully!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading configuration: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    gui = FileSelectorGUI(root)
    root.mainloop()
