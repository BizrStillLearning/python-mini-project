import customtkinter as ctk
import random
import json
import os

SCORE_FILE = "hangman_highscore.json"


class HangmanGame(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Hangman Pro V 3.2")
        self.geometry("600x800")
        self.resizable(False, False)

        self.categories = {
            "Programming": ["PYTHON", "JAVASCRIPT", "DATABASE", "ALGORITMA", "FRONTEND", "BACKEND", "GOLANG", "SWIFT"],
            "Anime": ["NARUTO", "ONEPIECE", "SHINGEKI", "DORAEMON", "PROMISED", "SOLOLEVELING", "JUJUTSU"],
            "K-Pop": ["TWICE", "NEXZ", "BLACKPINK", "STRAYKIDS", "AESPA", "NEWJEANS", "TREASURE"],
            "Kota": ["SURABAYA", "JAKARTA", "TOKYO", "LONDON", "PARIS", "NEWYORK", "SEOUL", "BANDUNG"],
            "Makanan": ["RENDANG", "SATE", "BURGER", "SUSHI", "RAMEN", "PIZZA", "NASIGORENG", "DIMSUM"]
        }

        self.current_category = ""
        self.target_word = ""
        self.guessed_letters = []
        self.attempts_left = 6
        self.score = 0
        self.highscore = self.load_highscore()
        self.game_active = False

        ctk.set_appearance_mode("dark")
        self.color_accent = "#33ff33"

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_start_screen()

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
        # Bersihkan Container
        for child in self.container.winfo_children():
            child.destroy()

        self.start_frame = ctk.CTkFrame(self.container, corner_radius=20, border_width=2,
                                        border_color=self.color_accent)
        self.start_frame.pack(pady=100, padx=50, fill="both", expand=True)

        ctk.CTkLabel(self.start_frame, text="HANGMAN", font=("Bahnschrift", 60, "bold"),
                     text_color=self.color_accent).pack(pady=(80, 10))
        ctk.CTkLabel(self.start_frame, text="PRO EDITION V 3.2", font=("Bahnschrift", 20), text_color="gray").pack(
            pady=10)

        ctk.CTkLabel(self.start_frame, text=f"HIGHSCORE: {self.highscore}", font=("Bahnschrift", 18, "bold"),
                     text_color="#ffcc00").pack(pady=30)

        ctk.CTkButton(self.start_frame, text="START GAME", font=("Bahnschrift", 20, "bold"),
                      fg_color=self.color_accent, text_color="black", height=60, width=250,
                      command=self.init_game_ui).pack(pady=20)

        ctk.CTkButton(self.start_frame, text="EXIT", font=("Bahnschrift", 16),
                      fg_color="#ff3333", height=40, width=150,
                      command=self.quit).pack(pady=10)

    def init_game_ui(self):
        for child in self.container.winfo_children():
            child.destroy()

        self.main_frame = ctk.CTkFrame(self.container, corner_radius=20, border_width=2, border_color=self.color_accent)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Dashboard Skor
        self.score_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.score_frame.pack(pady=5, fill="x")
        self.score_label = ctk.CTkLabel(self.score_frame, text=f"Score: 0", font=("Bahnschrift", 18))
        self.score_label.pack(side="left", padx=30)
        self.hi_score_label = ctk.CTkLabel(self.score_frame, text=f"Best: {self.highscore}", font=("Bahnschrift", 18),
                                           text_color="#ffcc00")
        self.hi_score_label.pack(side="right", padx=30)

        self.category_display = ctk.CTkLabel(self.main_frame, text="Category: ...", font=("Bahnschrift", 20, "bold"),
                                             text_color="#00ffff")
        self.category_display.pack(pady=5)

        # CANVAS DIPERKECIL
        self.canvas = ctk.CTkCanvas(self.main_frame, width=200, height=180, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=5)

        self.word_label = ctk.CTkLabel(self.main_frame, text="", font=("Consolas", 40, "bold"),
                                       text_color=self.color_accent)
        self.word_label.pack(pady=10)

        self.input_var = ctk.StringVar()
        self.input_var.trace_add("write", self.auto_capitalize)
        self.entry_input = ctk.CTkEntry(self.main_frame, textvariable=self.input_var, placeholder_text="?", width=60,
                                        height=60, font=("Bahnschrift", 30), justify="center")
        self.entry_input.pack(pady=10)
        self.entry_input.bind("<Return>", lambda e: self.make_guess())

        self.btn_guess = ctk.CTkButton(self.main_frame, text="GUESS", fg_color=self.color_accent, text_color="black",
                                       font=("Bahnschrift", 18, "bold"), command=self.make_guess)
        self.btn_guess.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=("Bahnschrift", 14))
        self.status_label.pack(pady=5)

        self.history_label = ctk.CTkLabel(self.main_frame, text="Used: ", font=("Bahnschrift", 12), text_color="gray")
        self.history_label.pack(pady=5)

        # Control Buttons
        self.ctrl_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.ctrl_frame.pack(pady=15)
        ctk.CTkButton(self.ctrl_frame, text="RESET", width=100, fg_color="#3b3b3b", command=self.reset_full_game).pack(
            side="left", padx=10)
        ctk.CTkButton(self.ctrl_frame, text="EXIT", width=100, fg_color="#ff3333", command=self.show_start_screen).pack(
            side="left", padx=10)

        self.start_new_game()

    def auto_capitalize(self, *args):
        val = self.input_var.get()
        if len(val) > 0:
            char = val[-1].upper()
            self.input_var.set(char if char.isalpha() else "")

    def start_new_game(self):
        self.current_category = random.choice(list(self.categories.keys()))
        self.target_word = random.choice(self.categories[self.current_category]).upper()
        self.guessed_letters = []
        self.attempts_left = 6
        self.game_active = True
        self.draw_hangman()
        self.update_display()
        self.entry_input.configure(state="normal")
        self.btn_guess.configure(state="normal", text="GUESS", fg_color=self.color_accent)
        self.category_display.configure(text=f"Category: {self.current_category}")
        self.status_label.configure(text="New Word Loaded!", text_color="gray")

    def reset_full_game(self):
        self.score = 0
        self.score_label.configure(text="Score: 0")
        self.start_new_game()

    def update_display(self):
        display_word = ""
        for char in self.target_word:
            display_word += (char if char in self.guessed_letters else "_") + " "
        self.word_label.configure(text=display_word.strip())
        self.history_label.configure(text=f"Used: {', '.join(sorted(self.guessed_letters))}")

    def make_guess(self):
        if not self.game_active: return
        guess = self.input_var.get()
        self.input_var.set("")
        if not guess or guess in self.guessed_letters: return
        self.guessed_letters.append(guess)
        if guess in self.target_word:
            self.status_label.configure(text=f"Yes! '{guess}' is correct.", text_color=self.color_accent)
        else:
            self.attempts_left -= 1
            self.draw_hangman()
            self.status_label.configure(text=f"Wrong! {self.attempts_left} left.", text_color="#ff3333")
        self.update_display()
        self.check_game_over()

    def check_game_over(self):
        if all(char in self.guessed_letters for char in self.target_word):
            self.score += 10 + (self.attempts_left * 2)
            self.score_label.configure(text=f"Score: {self.score}")
            self.save_highscore()
            self.hi_score_label.configure(text=f"Best: {self.highscore}")
            self.game_active = False
            self.status_label.configure(text="CORRECT! Next in 3s...", text_color="#00ff00")
            self.entry_input.configure(state="disabled")
            self.after(3000, self.start_new_game)
        elif self.attempts_left <= 0:
            self.game_active = False
            self.save_highscore()
            self.status_label.configure(text=f"GAME OVER!", text_color="#ff3333")
            self.word_label.configure(text=" ".join(self.target_word))
            self.btn_guess.configure(state="disabled", text="DEFEATED")

    def draw_hangman(self):
        self.canvas.delete("all")
        p = self.color_accent
        # Skala koordinat disesuaikan dengan canvas 200x180
        self.canvas.create_line(30, 160, 170, 160, fill="#555555", width=4)
        self.canvas.create_line(60, 160, 60, 20, fill="#555555", width=4)
        self.canvas.create_line(60, 20, 140, 20, fill="#555555", width=4)
        self.canvas.create_line(140, 20, 140, 40, fill="#ffcc00", width=2)

        c = self.color_accent
        if self.attempts_left <= 5: self.canvas.create_oval(125, 40, 155, 70, outline=c, width=3)
        if self.attempts_left <= 4: self.canvas.create_line(140, 70, 140, 120, fill=c, width=3)
        if self.attempts_left <= 3: self.canvas.create_line(140, 80, 120, 100, fill=c, width=3)
        if self.attempts_left <= 2: self.canvas.create_line(140, 80, 160, 100, fill=c, width=3)
        if self.attempts_left <= 1: self.canvas.create_line(140, 120, 120, 150, fill=c, width=3)
        if self.attempts_left <= 0: self.canvas.create_line(140, 120, 160, 150, fill=c, width=3)


if __name__ == "__main__":
    HangmanGame().mainloop()