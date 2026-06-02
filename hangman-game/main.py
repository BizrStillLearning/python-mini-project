import customtkinter as ctk
import random
import json
import os
import math
import winsound

SCORE_FILE = "hangman_highscore.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class HangmanGame(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🎮 Hangman Ultimate Edition")
        self.geometry("700x850")
        self.resizable(False, False)

        self.categories = {
            "Programming": [
                "PYTHON", "JAVASCRIPT", "DATABASE", "ALGORITMA",
                "FRONTEND", "BACKEND", "GOLANG", "SWIFT"
            ],
            "Anime": [
                "NARUTO", "ONEPIECE", "SHINGEKI", "DORAEMON",
                "PROMISED", "SOLOLEVELING", "JUJUTSU"
            ],
            "K-Pop": [
                "TWICE", "NEXZ", "BLACKPINK", "STRAYKIDS",
                "AESPA", "NEWJEANS", "TREASURE"
            ],
            "Kota": [
                "SURABAYA", "JAKARTA", "TOKYO", "LONDON",
                "PARIS", "NEWYORK", "SEOUL", "BANDUNG"
            ],
            "Makanan": [
                "RENDANG", "SATE", "BURGER", "SUSHI",
                "RAMEN", "PIZZA", "NASIGORENG", "DIMSUM"
            ]
        }

        self.category_colors = {
            "Programming": "#00ff99",
            "Anime": "#ff9900",
            "K-Pop": "#ff66b2",
            "Kota": "#33ccff",
            "Makanan": "#ffcc00"
        }

        self.current_category = ""
        self.target_word = ""
        self.guessed_letters = []

        self.attempts_left = 6
        self.score = 0
        self.lives = 3
        self.highscore = self.load_highscore()

        self.game_active = False
        self.keyboard_buttons = {}

        self.particles = []
        self.glow_phase = 0

        self.color_primary = "#00ff99"
        self.color_wrong = "#ff4d4d"
        self.color_bg = "#111111"

        self.configure(fg_color=self.color_bg)

        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.container.pack(fill="both", expand=True)

        self.bind("<Key>", self.handle_keypress)

        self.show_start_screen()

    def handle_keypress(self, event):
        if not self.game_active:
            return

        char = event.char.upper()

        if char in self.keyboard_buttons:
            btn = self.keyboard_buttons[char]
            if btn.cget("state") == "normal":
                self.make_guess(char)

    def load_highscore(self):
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, "r") as f:
                    return json.load(f).get("highscore", 0)
            except:
                return 0
        return 0

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open(SCORE_FILE, "w") as f:
                json.dump({"highscore": self.highscore}, f)

    def show_start_screen(self):
        for child in self.container.winfo_children():
            child.destroy()

        frame = ctk.CTkFrame(
            self.container,
            corner_radius=25,
            border_width=3,
            border_color=self.color_primary
        )
        frame.pack(expand=True, padx=60, pady=60, fill="both")

        title = ctk.CTkLabel(
            frame,
            text="🎮 HANGMAN",
            font=("Bahnschrift", 54, "bold"),
            text_color=self.color_primary
        )
        title.pack(pady=(80, 10))

        subtitle = ctk.CTkLabel(
            frame,
            text="ULTIMATE EDITION",
            font=("Bahnschrift", 20),
            text_color="gray"
        )
        subtitle.pack()

        high = ctk.CTkLabel(
            frame,
            text=f"🏆 HIGHSCORE : {self.highscore}",
            font=("Bahnschrift", 24, "bold"),
            text_color="#ffd700"
        )
        high.pack(pady=40)

        start_btn = ctk.CTkButton(
            frame,
            text="▶ START GAME",
            width=260,
            height=60,
            corner_radius=20,
            fg_color=self.color_primary,
            hover_color="#00cc77",
            text_color="black",
            font=("Bahnschrift", 22, "bold"),
            command=self.init_game_ui
        )
        start_btn.pack(pady=20)

        exit_btn = ctk.CTkButton(
            frame,
            text="EXIT",
            width=160,
            height=45,
            corner_radius=15,
            fg_color=self.color_wrong,
            hover_color="#cc0000",
            font=("Bahnschrift", 16, "bold"),
            command=self.quit
        )
        exit_btn.pack(pady=10)

    def init_game_ui(self):
        for child in self.container.winfo_children():
            child.destroy()

        self.main_frame = ctk.CTkFrame(
            self.container,
            corner_radius=25,
            fg_color="#181818",
            border_width=2,
            border_color=self.color_primary
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)

        self.score_label = ctk.CTkLabel(
            header,
            text=f"⭐ Score : {self.score}",
            font=("Bahnschrift", 18, "bold")
        )
        self.score_label.pack(side="left", padx=20)

        self.lives_label = ctk.CTkLabel(
            header,
            text="❤️" * self.lives,
            font=("Segoe UI Emoji", 20)
        )
        self.lives_label.pack(side="left", expand=True)

        self.high_label = ctk.CTkLabel(
            header,
            text=f"🏆 Best : {self.highscore}",
            text_color="#ffd700",
            font=("Bahnschrift", 18, "bold")
        )
        self.high_label.pack(side="right", padx=20)

        self.category_label = ctk.CTkLabel(
            self.main_frame,
            text="Category : ???",
            font=("Bahnschrift", 24, "bold"),
            text_color="#00ccf f"
        )
        self.category_label.pack(pady=5)

        self.canvas_container = ctk.CTkFrame(self.main_frame, width=280, height=200, fg_color="#101010",
                                             corner_radius=10)
        self.canvas_container.pack(pady=10)
        self.canvas_container.pack_propagate(False)

        self.canvas = ctk.CTkCanvas(
            self.canvas_container,
            bg="#101010",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.word_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.word_frame.pack(pady=5)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Bahnschrift", 16)
        )
        self.status_label.pack(pady=5)

        self.keyboard_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.keyboard_frame.pack(pady=5)

        self.create_keyboard()

        control = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        control.pack(pady=10)

        reset_btn = ctk.CTkButton(
            control,
            text="🔄 RESET",
            width=130,
            height=40,
            font=("Bahnschrift", 16, "bold"),
            fg_color="#444444",
            hover_color="#666666",
            command=self.reset_game
        )
        reset_btn.pack(side="left", padx=10)

        exit_btn = ctk.CTkButton(
            control,
            text="🏠 MENU",
            width=130,
            height=40,
            font=("Bahnschrift", 16, "bold"),
            fg_color=self.color_wrong,
            hover_color="#cc0000",
            command=self.show_start_screen
        )
        exit_btn.pack(side="left", padx=10)

        self.start_new_game()

    def create_keyboard(self):
        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]

        for row_letters in rows:
            row_frame = ctk.CTkFrame(self.keyboard_frame, fg_color="transparent")
            row_frame.pack(pady=3)

            for letter in row_letters:
                btn = ctk.CTkButton(
                    row_frame,
                    text=letter,
                    width=45,
                    height=45,
                    corner_radius=10,
                    font=("Bahnschrift", 18, "bold"),
                    fg_color="#2a2a2a",
                    hover_color="#444444",
                    command=lambda l=letter: self.make_guess(l)
                )
                btn.pack(side="left", padx=3)
                self.keyboard_buttons[letter] = btn

    def start_new_game(self):
        self.current_category = random.choice(list(self.categories.keys()))
        self.target_word = random.choice(self.categories[self.current_category]).upper()
        self.guessed_letters = []
        self.attempts_left = 6
        self.game_active = True

        cat_color = self.category_colors.get(self.current_category, "#00ccff")
        self.category_label.configure(
            text=f"📂 Category : {self.current_category}",
            text_color=cat_color
        )

        self.status_label.configure(text="Type on keyboard or click a letter...", text_color="gray")

        for btn in self.keyboard_buttons.values():
            btn.configure(state="normal", fg_color="#2a2a2a")

        self.update_word_display()
        self.animate_hangman()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.score_label.configure(text="⭐ Score : 0")
        self.lives_label.configure(text="❤️" * self.lives)
        self.start_new_game()

    def update_word_display(self, reveal_missed=False):
        for widget in self.word_frame.winfo_children():
            widget.destroy()

        for char in self.target_word:
            if char in self.guessed_letters:
                lbl = ctk.CTkLabel(
                    self.word_frame,
                    text=char,
                    font=("Consolas", 32, "bold"),
                    text_color=self.color_primary
                )
            elif reveal_missed:
                lbl = ctk.CTkLabel(
                    self.word_frame,
                    text=char,
                    font=("Consolas", 32, "bold"),
                    text_color=self.color_wrong
                )
            else:
                lbl = ctk.CTkLabel(
                    self.word_frame,
                    text="_",
                    font=("Consolas", 32, "bold"),
                    text_color="white"
                )
            lbl.pack(side="left", padx=5)

    def make_guess(self, guess):
        if not self.game_active:
            return

        if guess in self.guessed_letters:
            return

        self.guessed_letters.append(guess)
        btn = self.keyboard_buttons[guess]
        btn.configure(state="disabled")

        if guess in self.target_word:
            self.play_correct_sound()
            btn.configure(fg_color=self.color_primary)
            self.status_label.configure(
                text=f"✅ Correct! '{guess}' found!",
                text_color=self.color_primary
            )
        else:
            self.play_wrong_sound()
            self.attempts_left -= 1
            btn.configure(fg_color=self.color_wrong)
            self.status_label.configure(
                text=f"❌ Wrong! {self.attempts_left} attempts left",
                text_color=self.color_wrong
            )
            self.draw_hangman()

        self.update_word_display()
        self.check_game_over()

    def check_game_over(self):
        if all(char in self.guessed_letters for char in self.target_word):
            self.game_active = False
            bonus = self.attempts_left * 2
            self.score += 10 + bonus
            self.score_label.configure(text=f"⭐ Score : {self.score}")
            self.save_highscore()
            self.high_label.configure(text=f"🏆 Best : {self.highscore}")

            self.status_label.configure(
                text="🎉 YOU WIN! Next round in 3 seconds...",
                text_color=self.color_primary
            )
            self.play_win_sound()
            self.create_win_particles()
            self.disable_keyboard()
            self.after(3000, self.start_new_game)

        elif self.attempts_left <= 0:
            self.game_active = False
            self.play_lose_sound()
            self.disable_keyboard()

            self.update_word_display(reveal_missed=True)
            self.lives -= 1
            self.lives_label.configure(text="❤️" * self.lives + "🖤" * (3 - self.lives))

            if self.lives > 0:
                self.status_label.configure(
                    text=f"💀 Ouch! {self.lives} lives left. Next word in 3s...",
                    text_color=self.color_wrong
                )
                self.after(3000, self.start_new_game)
            else:
                self.status_label.configure(
                    text="💀 GAME OVER! Out of lives. Restarting in 3s...",
                    text_color=self.color_wrong
                )
                self.after(3000, self.reset_game)

    def disable_keyboard(self):
        for btn in self.keyboard_buttons.values():
            btn.configure(state="disabled")

    def play_correct_sound(self):
        winsound.Beep(900, 120)
        winsound.Beep(1200, 120)

    def play_wrong_sound(self):
        winsound.Beep(300, 250)

    def play_win_sound(self):
        winsound.Beep(900, 150)
        winsound.Beep(1200, 150)
        winsound.Beep(1500, 250)

    def play_lose_sound(self):
        winsound.Beep(500, 200)
        winsound.Beep(300, 300)

    def animate_hangman(self):
        self.glow_phase += 0.1
        glow = int(120 + math.sin(self.glow_phase) * 80)
        glow = max(50, min(255, glow))
        self.color_primary = f'#{0:02x}{glow:02x}{150:02x}'
        self.draw_hangman()

        if self.game_active:
            self.after(80, self.animate_hangman)

    def create_win_particles(self):
        self.particles = []
        for _ in range(40):
            particle = {
                "x": random.randint(30, 250),
                "y": random.randint(30, 180),
                "dx": random.uniform(-3, 3),
                "dy": random.uniform(-5, -1),
                "size": random.randint(4, 10),
                "life": random.randint(20, 40)
            }
            self.particles.append(particle)
        self.animate_particles()

    def animate_particles(self):
        self.draw_hangman()
        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["dy"] += 0.15
            p["life"] -= 1
            if p["life"] > 0:
                x = p["x"]
                y = p["y"]
                s = p["size"]
                self.canvas.create_oval(
                    x, y, x + s, y + s,
                    fill="#00ffff", outline=""
                )

        self.particles = [p for p in self.particles if p["life"] > 0]
        if len(self.particles) > 0:
            self.after(30, self.animate_particles)

    def draw_hangman(self):
        self.canvas.delete("all")
        c = self.color_primary

        for i in range(8, 0, -1):
            self.canvas.create_line(30, 180, 180, 180, fill="#003322", width=i + 4)
        self.canvas.create_line(30, 180, 180, 180, fill="#888888", width=6)

        self.canvas.create_line(60, 180, 60, 20, fill="#cccccc", width=6)

        self.canvas.create_line(60, 20, 160, 20, fill="#cccccc", width=6)

        self.canvas.create_line(160, 20, 160, 40, fill="#ffaa00", width=3)

        self.canvas.create_line(60, 50, 95, 20, fill="#666666", width=4)

        if self.attempts_left <= 5:
            for i in range(6, 0, -1):
                self.canvas.create_oval(135 - i, 40 - i, 185 + i, 90 + i, outline="#003322", width=2)
            self.canvas.create_oval(135, 40, 185, 90, outline=c, width=4)

        if self.attempts_left <= 4:
            self.canvas.create_line(160, 90, 160, 140, fill=c, width=4)

        if self.attempts_left <= 3:
            self.canvas.create_line(160, 105, 130, 125, fill=c, width=4)

        if self.attempts_left <= 2:
            self.canvas.create_line(160, 105, 190, 125, fill=c, width=4)

        if self.attempts_left <= 1:
            self.canvas.create_line(160, 140, 135, 175, fill=c, width=4)

        if self.attempts_left <= 0:
            self.canvas.create_line(160, 140, 185, 175, fill=c, width=4)

            self.canvas.create_line(148, 55, 155, 62, fill=self.color_wrong, width=2)
            self.canvas.create_line(155, 55, 148, 62, fill=self.color_wrong, width=2)
            self.canvas.create_line(165, 55, 172, 62, fill=self.color_wrong, width=2)
            self.canvas.create_line(172, 55, 165, 62, fill=self.color_wrong, width=2)

            self.canvas.create_arc(
                150, 65, 170, 80,
                start=0, extent=-180,
                style="arc",
                outline=self.color_wrong,
                width=2
            )


if __name__ == "__main__":
    app = HangmanGame()
    app.mainloop()