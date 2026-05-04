import customtkinter as ctk
from captcha.image import ImageCaptcha
import random
import string
from PIL import Image
import os
from datetime import datetime


class CaptchaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Access V 2.4 - Auto-Expiry Edition")
        self.geometry("500x650")
        self.resizable(False, False)

        self.attempts = 0
        self.max_attempts = 3
        self.lockout_time = 30
        self.expiry_time = 30
        self.current_expiry = self.expiry_time
        self.is_locked = False
        self.expiry_job = None

        ctk.set_appearance_mode("dark")
        self.color_success = "#33ff33"
        self.color_error = "#ff3333"

        self.generator = ImageCaptcha(width=300, height=100)
        self.current_captcha = ""
        self.captcha_path = "current_captcha.png"

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_captcha_page()

    def fade_in(self, widget, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(20, lambda: self.fade_in(widget, alpha))

    def slide_up(self, widget, current_y=600, target_y=40):
        if current_y > target_y:
            current_y -= 40
            widget.place(relx=0.5, y=current_y, anchor="n", relwidth=0.88, relheight=0.88)
            self.after(10, lambda: self.slide_up(widget, current_y, target_y))

    def show_captcha_page(self):
        self.attributes("-alpha", 0.0)
        for child in self.container.winfo_children(): child.destroy()

        self.captcha_frame = ctk.CTkFrame(self.container, corner_radius=20)
        self.captcha_frame.place(relx=0.5, y=600, anchor="n", relwidth=0.88, relheight=0.88)

        ctk.CTkLabel(self.captcha_frame, text="HUMAN VERIFICATION", font=("Bahnschrift", 22, "bold")).pack(pady=15)

        self.captcha_display = ctk.CTkLabel(self.captcha_frame, text="")
        self.captcha_display.pack(pady=10)

        self.expiry_bar = ctk.CTkProgressBar(self.captcha_frame, width=250, height=8)
        self.expiry_bar.set(1.0)
        self.expiry_bar.pack(pady=5)

        self.expiry_label = ctk.CTkLabel(self.captcha_frame, text=f"Expires in: {self.expiry_time}s",
                                         font=("Bahnschrift", 12))
        self.expiry_label.pack()

        self.btn_reload = ctk.CTkButton(self.captcha_frame, text="🔄 Reload", width=80, fg_color="transparent",
                                        border_width=1, command=self.generate_new_captcha)
        self.btn_reload.pack(pady=10)

        self.entry_input = ctk.CTkEntry(self.captcha_frame, placeholder_text="Type code here...", width=250, height=45,
                                        font=("Bahnschrift", 16), justify="center")
        self.entry_input.pack(pady=15)

        self.btn_verify = ctk.CTkButton(self.captcha_frame, text="ACCESS SYSTEM", fg_color=self.color_success,
                                        text_color="black", font=("Bahnschrift", 16, "bold"),
                                        command=self.verify_captcha)
        self.btn_verify.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.captcha_frame, text="", font=("Bahnschrift", 14))
        self.status_label.pack(pady=5)

        self.attempt_label = ctk.CTkLabel(self.captcha_frame, text=f"Attempts: 0/{self.max_attempts}",
                                          font=("Bahnschrift", 12), text_color="gray")
        self.attempt_label.pack(pady=5)

        self.generate_new_captcha()
        self.fade_in(self)
        self.slide_up(self.captcha_frame)

    def generate_new_captcha(self):
        if self.is_locked: return

        if self.expiry_job:
            self.after_cancel(self.expiry_job)

        chars = string.ascii_uppercase + string.digits
        self.current_captcha = ''.join(random.choice(chars) for _ in range(6))
        self.generator.write(self.current_captcha, self.captcha_path)

        img = Image.open(self.captcha_path)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 100))
        self.captcha_display.configure(image=ctk_img)
        self.entry_input.delete(0, 'end')

        self.current_expiry = self.expiry_time
        self.status_label.configure(text="New code generated", text_color="gray")
        self.update_expiry_timer()

    def update_expiry_timer(self):
        if not self.is_locked:
            if self.current_expiry > 0:
                self.current_expiry -= 1
                self.expiry_bar.set(self.current_expiry / self.expiry_time)
                self.expiry_label.configure(text=f"Expires in: {self.current_expiry}s")
                self.expiry_job = self.after(1000, self.update_expiry_timer)
            else:
                self.status_label.configure(text="⌛ Captcha expired! Refreshing...", text_color="#ffcc00")
                self.after(1000, self.generate_new_captcha)

    def verify_captcha(self):
        if self.is_locked: return

        if self.current_expiry <= 0:
            self.status_label.configure(text="❌ Code expired! Please wait for refresh.", text_color=self.color_error)
            return

        user_input = self.entry_input.get().strip().upper()
        if user_input == self.current_captcha:
            if self.expiry_job: self.after_cancel(self.expiry_job)  # Stop timer
            self.attempts = 0
            self.animate_transition(self.create_success_ui)
        else:
            self.attempts += 1
            self.attempt_label.configure(text=f"Attempts: {self.attempts}/{self.max_attempts}")
            if self.attempts >= self.max_attempts:
                self.start_lockout()
            else:
                self.status_label.configure(text="❌ Invalid Code. Try again.", text_color=self.color_error)
                self.generate_new_captcha()

    def start_lockout(self):
        self.is_locked = True
        if self.expiry_job: self.after_cancel(self.expiry_job)
        self.btn_verify.configure(state="disabled", fg_color="gray")
        self.btn_reload.configure(state="disabled")
        self.entry_input.configure(state="disabled")
        self.run_countdown(self.lockout_time)

    def run_countdown(self, seconds):
        if seconds > 0:
            self.status_label.configure(text=f"🛑 SYSTEM LOCKED! Wait {seconds}s", text_color=self.color_error)
            self.after(1000, lambda: self.run_countdown(seconds - 1))
        else:
            self.is_locked = False;
            self.attempts = 0
            self.btn_verify.configure(state="normal", fg_color=self.color_success)
            self.btn_reload.configure(state="normal");
            self.entry_input.configure(state="normal")
            self.attempt_label.configure(text=f"Attempts: 0/{self.max_attempts}")
            self.generate_new_captcha()

    def animate_transition(self, next_func):
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(20, lambda: self.animate_transition(next_func))
        else:
            next_func()
            self.fade_in(self)

    def create_success_ui(self):
        for child in self.container.winfo_children(): child.destroy()
        self.success_frame = ctk.CTkFrame(self.container, corner_radius=20, fg_color="#1a1a1a")
        self.success_frame.place(relx=0.5, y=600, anchor="n", relwidth=0.88, relheight=0.88)
        ctk.CTkLabel(self.success_frame, text="✓", font=("Arial", 80), text_color=self.color_success).pack(
            pady=(40, 10))
        ctk.CTkLabel(self.success_frame, text="ACCESS GRANTED", font=("Bahnschrift", 28, "bold"),
                     text_color=self.color_success).pack(pady=10)
        ctk.CTkLabel(self.success_frame, text="Welcome back, Administrator.", font=("Bahnschrift", 16),
                     text_color="gray").pack(pady=20)
        ctk.CTkButton(self.success_frame, text="LOGOUT", width=120, fg_color=self.color_error,
                      command=self.show_captcha_page).pack(pady=20)
        self.slide_up(self.success_frame)


if __name__ == "__main__":
    app = CaptchaApp()
    app.mainloop()