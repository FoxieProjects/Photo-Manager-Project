import os
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags, ImageOps

# --- DEFINISI TEMA & PRESET (Mendukung Light & Dark Mode) ---
# Format Tuple: (Warna saat Light Mode, Warna saat Dark Mode)
THEMES = {
    "Default": {
        "bg": ("#F0F0F0", "#0f0f1b"), 
        "sidebar": ("#E0E0E0", "#161625"), 
        "accent": ("#D0D0D0", "#2d2d44"), 
        "border": ("#BCBCBC", "#ffffff"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    },
    "Leaf Green": {
        "bg": ("#F0F0F0", "#0f1b13"), 
        "sidebar": ("#E0E0E0", "#16251b"), 
        "accent": ("#A5D6A7", "#2d4435"), 
        "border": ("#2E7D32", "#4e9a06"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    },
    "Red Velvet": {
        "bg": ("#F0F0F0", "#1b0f0f"), 
        "sidebar": ("#E0E0E0", "#251616"), 
        "accent": ("#EF9A9A", "#442d2d"), 
        "border": ("#C62828", "#a40000"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    },
    "Light Blue": {
        "bg": ("#F0F0F0", "#0f171b"), 
        "sidebar": ("#E0E0E0", "#161f25"), 
        "accent": ("#90CAF9", "#2d3b44"), 
        "border": ("#1565C0", "#3465a4"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    },
    "True Dark": {
        "bg": ("#F0F0F0", "#000000"), 
        "sidebar": ("#E0E0E0", "#0a0a0a"), 
        "accent": ("#333333", "#1a1a1a"), 
        "border": ("#555555", "#333333"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    },
    "Soft Purple": {
        "bg": ("#F0F0F0", "#150f1b"), 
        "sidebar": ("#E0E0E0", "#1e1625"), 
        "accent": ("#CE93D8", "#362d44"), 
        "border": ("#6A1B9A", "#75507b"),
        "text_main": ("#000000", "#ffffff"),
        "text_gray": ("#555555", "#a0a0a0")
    }
}

class AestheticPhotoSorter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- UPDATE JUDUL WINDOW ---
        self.title("Simple Photo Sorter | v1.0.1")
        self.geometry("1200x800")
        
        # State
        self.current_theme_name = "Default"
        self.src_dir = ""
        self.key_mappings = {}
        self.image_list = []
        self.current_index = 0
        self.history_stack = []
        self.photo_ref = None

        # Container Utama
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.show_main_view()
        self.bind("<Key>", self.handle_keypress)

    def get_colors(self):
        return THEMES[self.current_theme_name]

    def clear_view(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ===========================
    # MAIN VIEW
    # ===========================
    def show_main_view(self):
        self.clear_view()
        colors = self.get_colors()
        self.configure(fg_color=colors["bg"])
        
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0, minsize=280)
        self.main_container.grid_columnconfigure(1, weight=0, minsize=280)
        self.main_container.grid_columnconfigure(2, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, fg_color=colors["sidebar"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", pady=20, padx=15)

        ctk.CTkButton(header, text="⚙️", width=40, height=40, fg_color="transparent", 
                     hover_color=colors["accent"], text_color=colors["text_main"],
                     command=self.show_options_view).pack(side="left")

        ctk.CTkButton(header, text="↩️", width=40, height=40, fg_color="transparent",
                     hover_color=colors["accent"], text_color=colors["text_main"],
                     command=self.undo).pack(side="left", padx=10)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=colors["accent"]).pack(fill="x", padx=15, pady=(0, 20))

        # Konten Sidebar
        ctk.CTkLabel(self.sidebar, text="Source Folder", text_color=colors["text_main"], font=("", 13, "bold")).pack(anchor="w", padx=20)
        ctk.CTkButton(self.sidebar, text="Select Folder", fg_color=colors["accent"], text_color=colors["text_main"],
                     command=self.select_src).pack(fill="x", padx=20, pady=10)
        
        self.lbl_src_path = ctk.CTkLabel(self.sidebar, text=os.path.basename(self.src_dir) if self.src_dir else "No folder selected", 
                                        text_color=colors["text_gray"], font=("", 10), wraplength=220)
        self.lbl_src_path.pack(padx=20, pady=(0, 20), anchor="w")

        ctk.CTkLabel(self.sidebar, text="Target Folder & Keymaps", text_color=colors["text_main"], font=("", 13, "bold")).pack(anchor="w", padx=20)
        self.entry_key = ctk.CTkEntry(self.sidebar, placeholder_text="Key...", height=35, 
                                     fg_color=colors["accent"], text_color=colors["text_main"], border_width=0, justify="center")
        self.entry_key.pack(fill="x", padx=20, pady=10)
        self.entry_key.bind("<KeyPress>", self.capture_key)
        
        ctk.CTkButton(self.sidebar, text="Select Target & Add", fg_color=colors["accent"], text_color=colors["text_main"],
                     command=self.select_target_and_add).pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.sidebar, text="Active Keymaps", text_color=colors["text_main"], font=("", 13, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.map_container = ctk.CTkTextbox(self.sidebar, fg_color=colors["bg"], text_color=colors["text_main"],
                                           corner_radius=10, font=("Consolas", 11))
        self.map_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.update_map_container()

        # Panel Detail
        self.detail_frame = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], 
                                        border_color=colors["accent"], border_width=2, corner_radius=15)
        self.detail_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=20)
        ctk.CTkLabel(self.detail_frame, text="Detail", text_color=colors["text_main"], font=("", 18, "bold")).pack(pady=(30, 20))

        self.metadata_display = {}
        for field in ["Name", "Size", "Dimension", "Date", "Camera", "ISO"]:
            f = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(f, text=f"{field}:", text_color=colors["text_gray"], width=80, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(f, text="-", text_color=colors["text_main"], anchor="w", wraplength=150)
            lbl.pack(side="left", fill="x", expand=True)
            self.metadata_display[field] = lbl

        # Preview
        self.preview_container = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], 
                                             border_color=colors["border"], border_width=2, corner_radius=15)
        self.preview_container.grid(row=0, column=2, sticky="nsew", padx=(0, 20), pady=20)
        self.img_label = ctk.CTkLabel(self.preview_container, text="")
        self.img_label.pack(expand=True, fill="both", padx=10, pady=10)

        if self.image_list: self.show_photo()

    # ===========================
    # OPTIONS VIEW
    # ===========================
    def show_options_view(self):
        self.clear_view()
        colors = self.get_colors()
        self.configure(fg_color=colors["bg"])
        
        self.main_container.grid_columnconfigure(0, weight=0, minsize=210)
        self.main_container.grid_columnconfigure(1, weight=1)

        opt_sidebar = ctk.CTkFrame(self.main_container, fg_color=colors["sidebar"], corner_radius=0)
        opt_sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(opt_sidebar, text="⚙️ OPTIONS", text_color=colors["text_main"], font=("", 16, "bold")).pack(pady=30)

        for txt, cmd in [("PERSONALIZATION", "personal"), ("FOLLOW ME?", "follow"), ("ABOUT", "about")]:
            ctk.CTkButton(opt_sidebar, text=txt, fg_color=colors["accent"], text_color=colors["text_main"],
                         height=40, command=lambda t=cmd: self.show_opt_content(t)).pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(opt_sidebar, text="⬅️ EXIT", fg_color="transparent", text_color=colors["text_main"],
                     hover_color="#ff4444", command=self.show_main_view).pack(side="bottom", fill="x", padx=15, pady=20)

        self.opt_content_area = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
        self.opt_content_area.grid(row=0, column=1, sticky="nsew")
        self.show_opt_content("personal")

    def show_opt_content(self, target):
        for w in self.opt_content_area.winfo_children(): w.destroy()
        colors = self.get_colors()
        
        if target == "personal":
            ctk.CTkLabel(self.opt_content_area, text="No Light UI?", text_color=colors["text_main"], font=("", 16)).pack(anchor="w", padx=30, pady=(40, 5))
            self.switch_light = ctk.CTkSwitch(self.opt_content_area, text="", command=self.toggle_light_ui, 
                                             progress_color="#29abe0", text_color=colors["text_main"])
            self.switch_light.pack(anchor="w", padx=30)
            if ctk.get_appearance_mode() == "Dark": self.switch_light.select()
            
            ctk.CTkLabel(self.opt_content_area, text="Basically makes the theme dark to save battery...", 
                        text_color=colors["text_gray"], font=("", 11), justify="left").pack(anchor="w", padx=30, pady=5)

            ctk.CTkLabel(self.opt_content_area, text="More Theme", text_color=colors["text_main"], font=("", 16)).pack(anchor="w", padx=30, pady=(30, 5))
            self.theme_combo = ctk.CTkComboBox(self.opt_content_area, values=list(THEMES.keys()), command=self.change_theme_preset,
                                              fg_color=colors["accent"], text_color=colors["text_main"])
            self.theme_combo.set(self.current_theme_name)
            self.theme_combo.pack(anchor="w", padx=30, pady=10)
            if ctk.get_appearance_mode() == "Light": self.theme_combo.configure(state="disabled")

        elif target == "follow":
            socials = [("Instagram", "@yo.shoot__", "https://instagram.com/yo.shoot__"),
                       ("TikTok", "@yo.shoot__", "https://tiktok.com/@yo.shoot__"),
                       ("Twitter (X)", "@FoxieSan__", "https://twitter.com/FoxieSan__")]
            for icon, user, link in socials:
                f = ctk.CTkFrame(self.opt_content_area, fg_color="transparent")
                f.pack(fill="x", padx=30, pady=10)
                ctk.CTkLabel(f, text=f"📱 {icon}: {user}", text_color=colors["text_main"], font=("", 15)).pack(side="left")
                ctk.CTkButton(f, text="Visit", width=60, fg_color=colors["accent"], text_color=colors["text_main"],
                             command=lambda l=link: webbrowser.open(l)).pack(side="right")

            ctk.CTkLabel(self.opt_content_area, text="Donate?", text_color=colors["text_main"], font=("", 16, "bold")).pack(anchor="w", padx=30, pady=(30, 10))
            ctk.CTkButton(self.opt_content_area, text="☕ Support on Ko-fi", fg_color="#29abe0", text_color="white",
                         command=lambda: webbrowser.open("https://ko-fi.com/foxievarzy")).pack(fill="x", padx=30, pady=5)
            ctk.CTkButton(self.opt_content_area, text="🦊 Support on Saweria", fg_color="#faae2b", text_color="black",
                         command=lambda: webbrowser.open("https://saweria.co/FoxieVarzy")).pack(fill="x", padx=30, pady=5)

        elif target == "about":
            about_text = ("HI! Here's a bit about this software\n\nThis software is my first solo project, and it functions as a photo sorter. The idea is simple: you can sort your photos just by pressing keys on your keyboard, and the software moves them to the specified folders. Pretty simple, right? Yes, it is! I came up with this idea because I was bored of sorting my photos manually, so I just built this. That's all there is to it—I hope you find it helpful!"
                          "\n\nCreated by Agoy with help of Gemini")
            ctk.CTkLabel(self.opt_content_area, text=about_text, text_color=colors["text_main"], font=("", 13), 
                        justify="left", wraplength=500).pack(padx=30, pady=40, anchor="nw")

    # ===========================
    # CORE LOGIC
    # ===========================
    def toggle_light_ui(self):
        if self.switch_light.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
            self.current_theme_name = "Default"
        self.show_options_view()

    def change_theme_preset(self, choice):
        self.current_theme_name = choice
        self.show_options_view()

    def get_photo_metadata(self, path):
        data = {"Name": os.path.basename(path), "Size": "-", "Dimension": "-", "Date": "-", "Camera": "-", "ISO": "-"}
        try:
            data["Size"] = f"{os.path.getsize(path)/(1024*1024):.2f} MB"
            with Image.open(path) as img:
                data["Dimension"] = f"{img.size[0]} x {img.size[1]} px"
                exif = img._getexif()
                if exif:
                    e = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
                    data["Date"] = e.get("DateTimeOriginal", e.get("DateTime", "-"))
                    data["Camera"] = f"{e.get('Make','')} {e.get('Model','')}".strip() or "-"
                    data["ISO"] = str(e.get("ISOSpeedRatings", "-"))
        except: pass
        return data

    def show_photo(self):
        if self.current_index < len(self.image_list):
            img_path = os.path.join(self.src_dir, self.image_list[self.current_index])
            meta = self.get_photo_metadata(img_path)
            for k, v in meta.items(): self.metadata_display[k].configure(text=v)
            with Image.open(img_path) as tmp:
             raw = ImageOps.exif_transpose(tmp).copy()
            self.update_idletasks()
            cw, ch = self.preview_container.winfo_width()-40, self.preview_container.winfo_height()-40
            s = min(cw/max(raw.size[0],1), ch/max(raw.size[1],1))
            self.photo_ref = ctk.CTkImage(light_image=raw, dark_image=raw, size=(int(raw.size[0]*s), int(raw.size[1]*s)))
            self.img_label.configure(image=self.photo_ref, text="")
        else:
            self.img_label.configure(image=None, text="✅ ALL SORTED")

    def select_src(self):
        p = filedialog.askdirectory()
        if p:
            self.src_dir = p
            self.lbl_src_path.configure(text=os.path.basename(p))
            self.image_list = [f for f in os.listdir(p) if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))]
            self.current_index = 0
            self.show_photo()

    def capture_key(self, event):
        k = event.keysym.lower()
        self.entry_key.delete(0, "end"); self.entry_key.insert(0, k)
        return "break"

    def select_target_and_add(self):
        k = self.entry_key.get()
        if not k: return
        p = filedialog.askdirectory()
        if p:
            self.key_mappings[k] = p
            self.update_map_container()
            self.entry_key.delete(0, "end"); self.focus_set()

    def update_map_container(self):
        self.map_container.configure(state="normal")
        self.map_container.delete("1.0", "end")
        for k, v in self.key_mappings.items(): self.map_container.insert("end", f"[{k.upper()}] -> {os.path.basename(v)}\n")
        self.map_container.configure(state="disabled")

    def handle_keypress(self, event):
        # Mencegah perpindahan foto jika sedang mengetik di Entry Key
        if self.focus_get() == self.entry_key: return
        k = event.keysym.lower()
        if k in self.key_mappings and self.current_index < len(self.image_list):
            src = os.path.join(self.src_dir, self.image_list[self.current_index])
            dst = os.path.join(self.key_mappings[k], self.image_list[self.current_index])
            try:
                shutil.move(src, dst)
                self.history_stack.append((src, dst))
                self.current_index += 1; self.show_photo()
            except Exception as e: messagebox.showerror("Error", str(e))

    def undo(self):
        if not self.history_stack: return
        s, d = self.history_stack.pop()
        if os.path.exists(d):
            shutil.move(d, s)
            self.current_index -= 1; self.show_photo()

if __name__ == "__main__":
    app = AestheticPhotoSorter()
    app.mainloop()