import customtkinter as ctk
from datetime import datetime, timedelta
import pytz
import pygame
import os


class ModernClock(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Clock Pro V 2.5")
        self.geometry("850x700")

        pygame.mixer.init()

        self.daftar_warna = ["#33ff33", "#ff3333", "#3399ff", "#ff33cc", "#ffff33", "#00ffff"]
        self.warna_aktif = self.daftar_warna[0]
        self.timezone_aktif = "Asia/Jakarta"
        self.is_fullscreen = False

        self.sw_running = False
        self.sw_current_time = timedelta()

        self.t_jam, self.t_menit, self.t_detik = 0, 0, 0
        self.timer_running = False
        self.timer_remaining = timedelta()

        self.list_timezone = {
            "Surabaya (WIB)": "Asia/Jakarta",
            "Tokyo (JST)": "Asia/Tokyo",
            "London (GMT)": "Europe/London",
            "New York (EST)": "America/New_York"
        }

        self.setup_ui()
        self.bind_events()
        self.update_main()

    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=self.warna_aktif)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        self.tab_clock = self.tabview.add("CLOCK")
        self.tab_stopwatch = self.tabview.add("STOPWATCH")
        self.tab_timer = self.tabview.add("TIMER")

        self.time_label = ctk.CTkLabel(self.tab_clock, text="00:00:00", font=("Bahnschrift", 130, "bold"),
                                       text_color=self.warna_aktif)
        self.time_label.pack(expand=True)
        self.date_label = ctk.CTkLabel(self.tab_clock, text="", font=("Bahnschrift", 25), text_color="gray")
        self.date_label.pack(pady=10)

        self.sw_label = ctk.CTkLabel(self.tab_stopwatch, text="00:00:00.00", font=("Bahnschrift", 110, "bold"),
                                     text_color=self.warna_aktif)
        self.sw_label.pack(expand=True)
        sw_btn_frame = ctk.CTkFrame(self.tab_stopwatch, fg_color="transparent")
        sw_btn_frame.pack(pady=20)
        self.sw_start_btn = ctk.CTkButton(sw_btn_frame, text="START", command=self.toggle_stopwatch,
                                          fg_color=self.warna_aktif, text_color="black",
                                          font=("Bahnschrift", 18, "bold"))
        self.sw_start_btn.pack(side="left", padx=10)
        ctk.CTkButton(sw_btn_frame, text="RESET", command=self.reset_stopwatch).pack(side="left", padx=10)

        self.timer_label = ctk.CTkLabel(self.tab_timer, text="00:00:00", font=("Bahnschrift", 110, "bold"),
                                        text_color=self.warna_aktif)
        self.timer_label.pack(pady=20)

        t_ctrl_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        t_ctrl_frame.pack(pady=10)

        def create_adj(parent, label, attr, max_v):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(side="left", padx=25)
            ctk.CTkButton(f, text="▲", width=45, command=lambda: self.adj_timer(attr, 1, max_v)).pack()
            ctk.CTkLabel(f, text=label, font=("Bahnschrift", 14)).pack()
            ctk.CTkButton(f, text="▼", width=45, command=lambda: self.adj_timer(attr, -1, max_v)).pack()

        create_adj(t_ctrl_frame, "HRS", "t_jam", 23)
        create_adj(t_ctrl_frame, "MIN", "t_menit", 59)
        create_adj(t_ctrl_frame, "SEC", "t_detik", 59)

        t_btn_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        t_btn_frame.pack(pady=30)
        self.t_start_btn = ctk.CTkButton(t_btn_frame, text="START", command=self.toggle_timer,
                                         fg_color=self.warna_aktif, text_color="black",
                                         font=("Bahnschrift", 18, "bold"))
        self.t_start_btn.pack(side="left", padx=10)
        ctk.CTkButton(t_btn_frame, text="RESET", command=self.reset_timer).pack(side="left", padx=10)

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(pady=20)

        self.tz_menu = ctk.CTkOptionMenu(self.footer, values=list(self.list_timezone.keys()), command=self.ubah_tz,
                                         button_color=self.warna_aktif, text_color="white")
        self.tz_menu.pack(side="left", padx=20)

        self.picker_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.picker_frame.pack(side="left", padx=10)
        for w in self.daftar_warna:
            ctk.CTkButton(self.picker_frame, text="", width=28, height=28, corner_radius=14, fg_color=w, hover_color=w,
                          command=lambda c=w: self.ubah_warna(c)).pack(side="left", padx=4)

    def toggle_stopwatch(self):
        self.sw_running = not self.sw_running
        self.sw_start_btn.configure(text="PAUSE" if self.sw_running else "START")
        if self.sw_running: self.last_sw_tick = datetime.now()

    def reset_stopwatch(self):
        self.sw_running = False
        self.sw_current_time = timedelta()
        self.sw_label.configure(text="00:00:00.00")
        self.sw_start_btn.configure(text="START")

    # --- LOGIKA TIMER ---
    def adj_timer(self, attr, val, max_v):
        if not self.timer_running:
            cur = getattr(self, attr)
            setattr(self, attr, (cur + val) % (max_v + 1))
            self.timer_remaining = timedelta(hours=self.t_jam, minutes=self.t_menit, seconds=self.t_detik)
            self.update_t_label()

    def toggle_timer(self):
        if self.timer_remaining.total_seconds() > 0:
            self.timer_running = not self.timer_running
            self.t_start_btn.configure(text="PAUSE" if self.timer_running else "START")
            self.last_t_tick = datetime.now()

    def reset_timer(self):
        self.timer_running = False
        self.t_jam, self.t_menit, self.t_detik = 0, 0, 0
        self.timer_remaining = timedelta()
        self.update_t_label()
        self.t_start_btn.configure(text="START")
        self.timer_label.configure(text_color=self.warna_aktif)
        pygame.mixer.music.stop()

    def update_t_label(self):
        ts = int(self.timer_remaining.total_seconds())
        self.timer_label.configure(text=f"{ts // 3600:02d}:{(ts % 3600) // 60:02d}:{ts % 60:02d}")

    def update_main(self):
        tz = pytz.timezone(self.timezone_aktif)
        now = datetime.now(tz)
        self.time_label.configure(text=now.strftime('%H:%M:%S'))
        self.date_label.configure(text=now.strftime('%A, %d %B %Y'))

        if self.sw_running:
            tick = datetime.now()
            self.sw_current_time += (tick - self.last_sw_tick)
            self.last_sw_tick = tick
            ts = self.sw_current_time.total_seconds()
            self.sw_label.configure(
                text=f"{int(ts // 3600):02d}:{int((ts % 3600) // 60):02d}:{int(ts % 60):02d}.{int((ts % 1) * 100):02d}")

        if self.timer_running:
            tick = datetime.now()
            self.timer_remaining -= (tick - self.last_t_tick)
            self.last_t_tick = tick
            if self.timer_remaining.total_seconds() <= 0:
                self.timer_remaining = timedelta();
                self.timer_running = False
                self.timer_label.configure(text_color="#ff3333")
                if os.path.exists("assets/alarm.mp3"):
                    pygame.mixer.music.load("assets/alarm.mp3");
                    pygame.mixer.music.play(-1)
            self.update_t_label()

        self.after(10, self.update_main)

    def ubah_warna(self, c):
        self.warna_aktif = c
        self.tabview.configure(segmented_button_selected_color=c)
        for lbl in [self.time_label, self.sw_label, self.timer_label]: lbl.configure(text_color=c)
        for btn in [self.sw_start_btn, self.t_start_btn]: btn.configure(fg_color=c)
        self.tz_menu.configure(button_color=c)

    def ubah_tz(self, p):
        self.timezone_aktif = self.list_timezone[p]

    def bind_events(self):
        self.bind("<f>", lambda e: self.toggle_fs());
        self.bind("<F>", lambda e: self.toggle_fs())

    def toggle_fs(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)


if __name__ == "__main__":
    ModernClock().mainloop()