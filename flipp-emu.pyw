import tkinter as tk
from PIL import Image, ImageTk, ImageSequence, ImageEnhance
import os, random

Image.MAX_IMAGE_PIXELS = None

class FlipperSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Flipper Zero")
        self.root.geometry("320x170")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.dolphin_dir = "dolphin"
        self.menu_dir = "sysmenu"

        self.menu_items = [
            "momentum",
            "settings",
            "apps",
            "subgz",
            "rfid",
            "nfc",
            "infrared",
            "gpio",
            "ibutton",
            "badkb",
            "u2f"
        ]
        self.index = 0

        self.container = tk.Frame(root, width=320, height=170, bg="black", bd=0, highlightthickness=0)
        self.container.pack_propagate(False)
        self.container.pack()

        self.screen = tk.Label(self.container, bg="black", bd=0)
        self.screen.pack(expand=True, fill="both")

        self.frames = []
        self.durations = []
        self.frame_idx = 0
        self.loop_id = None

        if not os.path.exists(self.dolphin_dir) or not os.path.exists(self.menu_dir):
            self.show_error()
        else:
            self.root.after(100, self.load_random_dolphin)

    def show_error(self):
        self.screen.config(text="no FuriOS found!", fg="orange", bg="black", font=("Haxcorp", 14), anchor="w")

    def load_random_dolphin(self):
        gifs = [os.path.join(self.dolphin_dir, f) for f in os.listdir(self.dolphin_dir) if f.lower().endswith(".gif")]
        if not gifs:
            self.show_lockscreen()
            return

        chosen_gif = random.choice(gifs)

        try:
            with Image.open(chosen_gif) as img:
                self.frames = []
                self.durations = []
                for frame in ImageSequence.Iterator(img):
                    d = frame.info.get('duration', 100)
                    d = max(d, 100) * 2
                    self.durations.append(d)

                    c = Image.new("RGBA", (320, 170), (0, 0, 0, 255))
                    r = frame.copy().convert("RGBA").resize((320, 170), Image.NEAREST)

                    enhancer = ImageEnhance.Color(r)
                    r = enhancer.enhance(1.5)

                    c.paste(r, (0, 0), r)
                    self.frames.append(ImageTk.PhotoImage(c))

            if self.frames:
                self.animate_dolphin()
                self.root.after(4000, self.show_lockscreen)
            else:
                self.show_lockscreen()
        except:
            self.show_lockscreen()

    def animate_dolphin(self):
        if not self.frames: return
        self.screen.config(image=self.frames[self.frame_idx])
        delay = self.durations[self.frame_idx]
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.loop_id = self.root.after(delay, self.animate_dolphin)

    def show_lockscreen(self):
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None

        self.frames = []
        path = os.path.join(self.menu_dir, "lockscreen.png")
        try:
            img = Image.open(path).convert("RGBA").resize((320, 170), Image.NEAREST)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.5)
            self.lock_img = ImageTk.PhotoImage(img)
            self.screen.config(image=self.lock_img)
        except:
            self.screen.config(image='', text="LOCKED", fg="white")

        self.root.bind("<Return>", lambda e: self.activate_menu())
        self.root.bind("<z>", lambda e: self.activate_menu())
        self.root.bind("<Z>", lambda e: self.activate_menu())

    def activate_menu(self):
        self.root.unbind("<Return>")
        self.root.unbind("<z>")
        self.root.unbind("<Z>")
        self.root.bind("<Left>", lambda e: self.move(-1))
        self.root.bind("<Right>", lambda e: self.move(1))
        self.update_menu()

    def update_menu(self):
        item = self.menu_items[self.index]
        path = os.path.join(self.menu_dir, f"{item}.png")
        try:
            img = Image.open(path).convert("RGBA").resize((320, 170), Image.NEAREST)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.5)
            self.current_img = ImageTk.PhotoImage(img)
            self.screen.config(image=self.current_img)
        except:
            self.screen.config(image='', text=f"MISSING: {item}", fg="white")

    def move(self, d):
        self.index = (self.index + d) % len(self.menu_items)
        self.update_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlipperSimulator(root)
    root.mainloop()
