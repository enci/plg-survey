#!/usr/bin/env python3
"""
Manual Thematic Coding Application
TkInter GUI for manually assigning thematic codes to survey responses
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Set

# Theme definitions with colors (tab10 colormap RGB values, normalized to 0-255)
THEMES = {
    "Control & Flexibility": {"color": "#1f77b4", "rgb": (31, 119, 180)},
    "Time & Efficiency": {"color": "#ff7f0e", "rgb": (255, 127, 14)},
    "Integration & Workflow": {"color": "#2ca02c", "rgb": (44, 160, 44)},
    "Technical Barriers": {"color": "#d62728", "rgb": (214, 39, 40)},
    "Designer Accessibility": {"color": "#9467bd", "rgb": (148, 103, 189)},
    "Debugging & Understanding": {"color": "#8c564b", "rgb": (140, 86, 75)},
    "Quality & Consistency": {"color": "#e377c2", "rgb": (227, 119, 194)},
    "Content Mixing": {"color": "#7f7f7f", "rgb": (127, 127, 127)},
    "Documentation & Learning": {"color": "#bcbd22", "rgb": (188, 189, 34)},
}


class ThematicCodingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thematic Coding - Manual Code Assignment")
        self.root.geometry("1200x800")
        
        # Data structures
        self.responses = []  # List of response dicts with hash, response, role, experience
        self.coded_answers = {}  # {hash: set of assigned theme names}
        self.current_index = 0
        self.data_dir = Path(__file__).parent
        
        # Setup UI
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Create the main UI layout"""
        # Top menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Responses", command=self.load_data)
        file_menu.add_command(label="Save Codes", command=self.save_codes)
        file_menu.add_command(label="Export to JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All Codes", command=self.clear_all_codes)
        edit_menu.add_command(label="Manage Themes", command=self.open_theme_manager)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel: Response list and details
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Responses", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.response_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            height=20,
            width=50,
            font=("Arial", 11),
            selectmode=tk.SINGLE
        )
        self.response_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.response_listbox.bind('<<ListboxSelect>>', self.on_response_select)
        scrollbar.config(command=self.response_listbox.yview)
        
        # Response details panel
        details_frame = ttk.LabelFrame(left_frame, text="Response Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(details_frame, text="Response:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.response_text = tk.Text(details_frame, height=4, width=50, wrap=tk.WORD, font=("Arial", 11))
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.response_text.config(state=tk.DISABLED)
        
        # Role and Experience
        meta_frame = ttk.Frame(details_frame)
        meta_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(meta_frame, text="Role:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.role_label = ttk.Label(meta_frame, text="", font=("Arial", 10), foreground="gray")
        self.role_label.pack(side=tk.LEFT, padx=(5, 20))
        ttk.Label(meta_frame, text="Experience:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.exp_label = ttk.Label(meta_frame, text="", font=("Arial", 10), foreground="gray")
        self.exp_label.pack(side=tk.LEFT, padx=5)
        
        # Hash display
        hash_frame = ttk.Frame(details_frame)
        hash_frame.pack(fill=tk.X)
        ttk.Label(hash_frame, text="Hash:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.hash_label = ttk.Label(hash_frame, text="", foreground="gray", font=("Courier", 9))
        self.hash_label.pack(side=tk.LEFT, padx=5)
        
        # Right panel: Theme assignment buttons
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Assigned Codes", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Currently assigned codes display
        assigned_frame = ttk.LabelFrame(right_frame, text="Selected Codes for This Response", padding=10)
        assigned_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 10))
        
        self.assigned_text = tk.Text(assigned_frame, height=4, width=30, wrap=tk.WORD, font=("Arial", 11))
        self.assigned_text.pack(fill=tk.BOTH, expand=True)
        self.assigned_text.config(state=tk.DISABLED)
        
        # Clear codes for current response
        ttk.Button(assigned_frame, text="Clear Codes for This Response", command=self.clear_current_codes).pack(fill=tk.X, pady=(10, 0))
        
        # Theme buttons
        ttk.Label(right_frame, text="Click to Toggle Code Assignment", font=("Arial", 10, "italic")).pack(anchor=tk.W, pady=(10, 5))
        
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        self.theme_buttons = {}
        for theme_name, theme_info in THEMES.items():
            color = theme_info["color"]
            btn = tk.Button(
                button_frame,
                text=theme_name,
                bg=color,
                fg=color,
                font=("Arial", 11, "bold"),
                height=3,
                command=lambda t=theme_name: self.toggle_theme(t),
                relief=tk.RAISED,
                bd=2,
                activebackground="#333",
                activeforeground=color
            )
            btn.pack(fill=tk.X, pady=4, padx=5)
            self.theme_buttons[theme_name] = btn
        
        # Bottom status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 11)
        )
        self.status_label.pack(fill=tk.X)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(nav_frame, text="← Previous", command=self.prev_response).pack(side=tk.LEFT, padx=5)
        self.progress_label = ttk.Label(nav_frame, text="", font=("Arial", 11))
        self.progress_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(nav_frame, text="Next →", command=self.next_response).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Save & Exit", command=self.save_and_exit).pack(side=tk.RIGHT, padx=5)
        
    def load_data(self):
        """Load responses and existing codes from JSON files"""
        answers_file = self.data_dir / "answers_input.json"
        codes_file = self.data_dir / "coded_answers.json"
        
        try:
            # Load responses
            if answers_file.exists():
                with open(answers_file, 'r', encoding='utf-8') as f:
                    self.responses = json.load(f)
                self.status_label.config(text=f"Loaded {len(self.responses)} responses")
            else:
                messagebox.showerror("Error", f"Cannot find {answers_file}")
                return
            
            # Load existing codes
            if codes_file.exists():
                with open(codes_file, 'r', encoding='utf-8') as f:
                    codes_data = json.load(f)
                    # Build coded_answers dict from response hashes
                    for item in codes_data:
                        self.coded_answers[item['hash']] = set(item['assigned_codes'])
            
            # Populate listbox
            self.update_response_list()
            
            if self.responses:
                self.show_response(0)
            
        except Exception as e:
            messagebox.showerror("Error loading data", str(e))
    
    def update_response_list(self):
        """Update the response listbox"""
        self.response_listbox.delete(0, tk.END)
        for i, resp in enumerate(self.responses):
            # Show response text with coding status
            resp_hash = resp['hash']
            num_codes = len(self.coded_answers.get(resp_hash, set()))
            prefix = "✓ " if num_codes > 0 else "  "
            text = f"{prefix}[{i+1}/{len(self.responses)}] {resp['response'][:60]}..."
            self.response_listbox.insert(tk.END, text)
    
    def on_response_select(self, event):
        """Handle response list selection"""
        if self.response_listbox.curselection():
            index = self.response_listbox.curselection()[0]
            self.show_response(index)
    
    def show_response(self, index):
        """Display response and its current codes"""
        if index < 0 or index >= len(self.responses):
            return
        
        self.current_index = index
        resp = self.responses[index]
        
        # Update text display
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, resp['response'])
        self.response_text.config(state=tk.DISABLED)
        
        # Update metadata
        self.role_label.config(text=resp.get('role', 'N/A'))
        self.exp_label.config(text=resp.get('experience', 'N/A'))
        self.hash_label.config(text=resp['hash'])
        
        # Update assigned codes display
        assigned = self.coded_answers.get(resp['hash'], set())
        self.assigned_text.config(state=tk.NORMAL)
        self.assigned_text.delete(1.0, tk.END)
        if assigned:
            self.assigned_text.insert(1.0, "\n".join(sorted(assigned)))
        else:
            self.assigned_text.insert(1.0, "(No codes assigned)")
        self.assigned_text.config(state=tk.DISABLED)
        
        # Update button states
        for theme_name in THEMES:
            btn = self.theme_buttons[theme_name]
            if theme_name in assigned:
                btn.config(relief=tk.SUNKEN, bd=4)
            else:
                btn.config(relief=tk.RAISED, bd=2)
        
        # Update selection and progress
        self.response_listbox.selection_clear(0, tk.END)
        self.response_listbox.selection_set(index)
        self.response_listbox.see(index)
        self.progress_label.config(text=f"{index + 1} / {len(self.responses)}")
        self.update_status()
    
    def toggle_theme(self, theme_name):
        """Toggle a theme assignment for current response"""
        if not self.responses:
            return
        
        resp_hash = self.responses[self.current_index]['hash']
        
        if resp_hash not in self.coded_answers:
            self.coded_answers[resp_hash] = set()
        
        if theme_name in self.coded_answers[resp_hash]:
            self.coded_answers[resp_hash].remove(theme_name)
        else:
            self.coded_answers[resp_hash].add(theme_name)
        
        # Refresh display
        self.show_response(self.current_index)
        self.update_response_list()
    
    def clear_current_codes(self):
        """Clear all codes for the current response"""
        if not self.responses:
            return
        
        resp_hash = self.responses[self.current_index]['hash']
        if resp_hash in self.coded_answers:
            self.coded_answers[resp_hash].clear()
            self.show_response(self.current_index)
            self.update_response_list()
    
    def clear_all_codes(self):
        """Clear all codes for all responses"""
        if messagebox.askyesno("Confirm", "Clear all codes for all responses?"):
            self.coded_answers.clear()
            self.show_response(self.current_index)
            self.update_response_list()
    
    def prev_response(self):
        """Show previous response"""
        if self.current_index > 0:
            self.show_response(self.current_index - 1)
    
    def next_response(self):
        """Show next response"""
        if self.current_index < len(self.responses) - 1:
            self.show_response(self.current_index + 1)
    
    def update_status(self):
        """Update status bar with current progress"""
        if not self.responses:
            self.status_label.config(text="No responses loaded")
            return
        
        total = len(self.responses)
        coded = sum(1 for h in self.coded_answers if self.coded_answers[h])
        pct = (coded / total * 100) if total > 0 else 0
        
        self.status_label.config(
            text=f"Coded: {coded}/{total} ({pct:.1f}%) | Total codes assigned: {sum(len(c) for c in self.coded_answers.values())}"
        )
    
    def save_codes(self):
        """Save coded answers to JSON"""
        output_file = self.data_dir / "coded_answers.json"
        
        try:
            # Prepare output data
            output_data = []
            for resp in self.responses:
                resp_hash = resp['hash']
                assigned = sorted(self.coded_answers.get(resp_hash, set()))
                output_data.append({
                    'hash': resp_hash,
                    'response': resp['response'],
                    'role': resp.get('role'),
                    'experience': resp.get('experience'),
                    'assigned_codes': assigned
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Codes saved to {output_file}")
            self.status_label.config(text=f"Saved at {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error saving", str(e))
    
    def export_json(self):
        """Export coded answers in various formats"""
        file_path = filedialog.asksaveasfilename(
            initialdir=str(self.data_dir),
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            output_data = []
            for resp in self.responses:
                resp_hash = resp['hash']
                assigned = sorted(self.coded_answers.get(resp_hash, set()))
                output_data.append({
                    'hash': resp_hash,
                    'response': resp['response'],
                    'role': resp.get('role'),
                    'experience': resp.get('experience'),
                    'assigned_codes': assigned,
                    'num_codes': len(assigned)
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error exporting", str(e))
    
    def open_theme_manager(self):
        """Open theme management window"""
        ThemeManagerWindow(self.root, THEMES)
    
    def save_and_exit(self):
        """Save codes and exit"""
        self.save_codes()
        self.root.quit()


class ThemeManagerWindow(tk.Toplevel):
    """Window for managing themes"""
    def __init__(self, parent, themes):
        super().__init__(parent)
        self.title("Theme Manager")
        self.geometry("400x600")
        self.themes = themes
        
        # Title
        ttk.Label(self, text="Theme Definitions", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Scrollable frame with themes
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for theme_name, theme_info in themes.items():
            frame = ttk.Frame(scrollable_frame, relief=tk.GROOVE, borderwidth=1)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            color_box = tk.Label(frame, bg=theme_info["color"], width=4, height=2)
            color_box.pack(side=tk.LEFT, padx=5, pady=5)
            
            ttk.Label(frame, text=theme_name, font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5)
            ttk.Label(
                frame,
                text=f"Color: {theme_info['color']} | RGB: {theme_info['rgb']}",
                font=("Arial", 8),
                foreground="gray"
            ).pack(anchor=tk.W, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)


def main():
    root = tk.Tk()
    app = ThematicCodingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
