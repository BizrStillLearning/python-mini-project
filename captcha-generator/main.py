import customtkinter as ctk
from captcha.image import ImageCaptcha
import random
import string
from PIL import Image
import os


class CaptchaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Access V 2.1")
        self.geometry("500x550")
        self.resizable(False, False)

        # Tema & Warna
        ctk.set_appearance_mode("dark")
        self.color_success = "#33ff33"

        # Inisialisasi Captcha
        self.generator = ImageCaptcha(width=300, height=100)
        self.current_captcha = ""
        self.captcha_path = "current_captcha.png"

        # Container utama untuk menampung berbagai halaman (Frames)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_captcha_page()

    def show_captcha_page(self):
        # Bersihkan container jika ada isinya
        for child in self.container.winfo_children():
            child.destroy()

        # --- FRAME CAPTCHA ---
        self.captcha_frame = ctk.CTkFrame(self.container, corner_radius=20)
        self.captcha_frame.pack(pady=40, padx=30, fill="both", expand=True)

        ctk.CTkLabel(self.captcha_frame, text="HUMAN VERIFICATION",
                     font=("Bahnschrift", 22, "bold")).pack(pady=20)

        self.captcha_display = ctk.CTkLabel(self.captcha_frame, text="")
        self.captcha_display.pack(pady=10)

        ctk.CTkButton(self.captcha_frame, text="🔄 Reload", width=80,
                      fg_color="transparent", border_width=1,
                      command=self.generate_new_captcha).pack(pady=5)

        self.entry_input = ctk.CTkEntry(self.captcha_frame, placeholder_text="Type code here...",
                                        width=250, height=45, font=("Bahnschrift", 16), justify="center")
        self.entry_input.pack(pady=20)

        self.btn_verify = ctk.CTkButton(self.captcha_frame, text="ACCESS SYSTEM",
                                        fg_color=self.color_success, text_color="black",
                                        font=("Bahnschrift", 16, "bold"),
                                        command=self.verify_captcha)
        self.btn_verify.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.captcha_frame, text="", font=("Bahnschrift", 14))
        self.status_label.pack(pady=5)

        self.generate_new_captcha()

    def show_success_page(self):
        # Hapus halaman captcha
        for child in self.container.winfo_children():
            child.destroy()

        # --- FRAME SUKSES (HALAMAN SETELAH VERIFIKASI) ---
        self.success_frame = ctk.CTkFrame(self.container, corner_radius=20, fg_color="#1a1a1a")
        self.success_frame.pack(pady=40, padx=30, fill="both", expand=True)

        # Animasi Checkmark Sederhana (Teks)
        ctk.CTkLabel(self.success_frame, text="✓", font=("Arial", 80),
                     text_color=self.color_success).pack(pady=(40, 10))

        ctk.CTkLabel(self.success_frame, text="ACCESS GRANTED",
                     font=("Bahnschrift", 28, "bold"), text_color=self.color_success).pack(pady=10)

        ctk.CTkLabel(self.success_frame, text="Verification Successful.\nYou are now logged into the system.",
                     font=("Bahnschrift", 16), text_color="gray", justify="center").pack(pady=20)

        # Tombol kembali (untuk testing)
        ctk.CTkButton(self.success_frame, text="LOGOUT", width=120,
                      fg_color="#ff3333", command=self.show_captcha_page).pack(pady=20)

    def generate_new_captcha(self):
        chars = string.ascii_uppercase + string.digits
        self.current_captcha = ''.join(random.choice(chars) for _ in range(6))
        self.generator.write(self.current_captcha, self.captcha_path)

        img = Image.open(self.captcha_path)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 100))
        self.captcha_display.configure(image=ctk_img)
        self.entry_input.delete(0, 'end')

    def verify_captcha(self):
        user_input = self.entry_input.get().strip().upper()
        if user_input == self.current_captcha:
            self.show_success_page()
        else:
            self.status_label.configure(text="❌ Invalid Code. Try again.", text_color="#ff3333")
            self.generate_new_captcha()


if __name__ == "__main__":
    app = CaptchaApp()
    app.mainloop()