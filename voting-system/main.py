import customtkinter as ctk
import re
import csv
from datetime import datetime
from tkinter import filedialog
from database.db_config import (
    init_database, db_cast_vote, db_get_results, db_get_voters, db_reset_system
)


class VotingSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Voting System V 2.5 - Enterprise Audit Edition")
        self.geometry("600x700")
        self.resizable(False, False)

        self.admin_password = "admin123"
        self.color_accent = "#33ff33"
        self.is_admin_authenticated = False

        init_database()

        ctk.set_appearance_mode("dark")
        self.setup_ui()
        self.update_results()

    def setup_ui(self):
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_frame = ctk.CTkFrame(self.scroll_container, corner_radius=20, border_width=2,
                                       border_color=self.color_accent)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="VOTE YOUR LANGUAGE",
                     font=("Bahnschrift", 28, "bold"), text_color=self.color_accent).pack(pady=15)

        self.admin_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a", corner_radius=10)
        self.admin_btn_frame.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(self.admin_btn_frame, text="Admin:", font=("Bahnschrift", 12, "bold"),
                     text_color="gray").pack(side="left", padx=15, pady=10)

        self.btn_view_log = ctk.CTkButton(self.admin_btn_frame, text="🔐 View Logs", fg_color="#3b3b3b", width=100,
                                          command=lambda: self.request_admin_access("VIEW_LOGS"))
        self.btn_view_log.pack(side="left", padx=5, pady=10)

        self.btn_export = ctk.CTkButton(self.admin_btn_frame, text="📥 Export CSV", fg_color="#3a7ebf", width=100,
                                        command=self.execute_admin_export)

        self.btn_reset = ctk.CTkButton(self.admin_btn_frame, text="🗑️ Reset DB", fg_color="#ff3333", text_color="black",
                                       font=("Bahnschrift", 12, "bold"), width=100,
                                       command=lambda: self.request_admin_access("RESET_DB"))

        self.id_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.id_frame.pack(pady=15)
        ctk.CTkLabel(self.id_frame, text="Enter Voter ID (NIM):", font=("Bahnschrift", 14)).pack(side="left", padx=10)
        self.entry_voter_id = ctk.CTkEntry(self.id_frame, placeholder_text="e.g., 20251337037", width=180)
        self.entry_voter_id.pack(side="left")

        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(pady=10)

        self.vote_buttons = {}
        for lang in ["Python", "JavaScript", "Golang", "C++"]:
            btn = ctk.CTkButton(self.options_frame, text=lang, font=("Bahnschrift", 16, "bold"),
                                width=200, height=42, command=lambda l=lang: self.cast_vote(l))
            btn.pack(pady=4)
            self.vote_buttons[lang] = btn

        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.pack(pady=10, fill="x", padx=40)

        self.result_bars = {}
        self.result_labels = {}

        for lang in ["Python", "JavaScript", "Golang", "C++"]:
            row = ctk.CTkFrame(self.results_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)

            lbl = ctk.CTkLabel(row, text=f"{lang}: 0", font=("Bahnschrift", 14), width=100, anchor="w")
            lbl.pack(side="left")

            bar = ctk.CTkProgressBar(row, orientation="horizontal", height=12, progress_color=self.color_accent)
            bar.set(0)
            bar.pack(side="left", fill="x", expand=True, padx=10)

            self.result_labels[lang] = lbl
            self.result_bars[lang] = bar

        self.status_label = ctk.CTkLabel(self.main_frame, text="Please enter your strictly numeric NIM!",
                                         font=("Bahnschrift", 14), text_color="gray")
        self.status_label.pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="--- Encrypted Audit Log ---", font=("Bahnschrift", 12),
                     text_color="gray").pack(
            pady=(10, 0))
        self.log_box = ctk.CTkTextbox(self.main_frame, width=400, height=70, font=("Consolas", 12))
        self.log_box.pack(pady=5)
        self.log_box.insert("0.0", "🔒 Logs are encrypted (SHA-256). Admin login required.")
        self.log_box.configure(state="disabled")

    def cast_vote(self, lang):
        voter_id = self.entry_voter_id.get().strip()

        if not re.match(r"^\d{7,15}$", voter_id):
            self.status_label.configure(text="⚠️ Error: NIM must be 7-15 numeric digits!", text_color="#ffcc00")
            return

        result = db_cast_vote(voter_id, lang)

        if result == "SUCCESS":
            self.status_label.configure(text=f"✅ Vote successfully cast for {lang}!", text_color=self.color_accent)
            self.entry_voter_id.delete(0, 'end')
        elif result == "ALREADY_VOTED":
            self.status_label.configure(text=f"❌ NIM '{voter_id}' has already voted!", text_color="#ff3333")
        else:
            self.status_label.configure(text=f"⚠️ {result}", text_color="#ff3333")

        self.update_results()

    def update_results(self):
        data = db_get_results()
        total_votes = sum(data.values())

        for lang, count in data.items():
            if lang in self.result_labels:
                self.result_labels[lang].configure(text=f"{lang}: {count}")
                percentage = count / total_votes if total_votes > 0 else 0
                self.result_bars[lang].set(percentage)

    def request_admin_access(self, action_type):
        self.login_win = ctk.CTkToplevel(self)
        self.login_win.title("Admin Authentication Required")
        self.login_win.geometry("380x220")
        self.login_win.resizable(False, False)
        self.login_win.lift()
        self.login_win.focus_force()
        self.login_win.grab_set()

        msg = "Enter Admin Password to Reset System:" if action_type == "RESET_DB" else "Enter Admin Password to View Logs:"
        ctk.CTkLabel(self.login_win, text=msg, font=("Bahnschrift", 13, "bold"),
                     text_color="#ffcc00" if action_type == "RESET_DB" else "white").pack(pady=15)

        pass_entry = ctk.CTkEntry(self.login_win, placeholder_text="Password", show="*", width=200, justify="center")
        pass_entry.pack(pady=5)
        pass_entry.focus()

        pass_entry.bind("<Return>", lambda e: self.validate_admin_password(pass_entry.get(), action_type))

        btn_submit = ctk.CTkButton(self.login_win, text="Confirm", fg_color=self.color_accent, text_color="black",
                                   font=("Bahnschrift", 12, "bold"),
                                   command=lambda: self.validate_admin_password(pass_entry.get(), action_type))
        btn_submit.pack(pady=15)

    def validate_admin_password(self, password, action_type):
        if password == self.admin_password:
            self.login_win.destroy()

            self.is_admin_authenticated = True

            # Memunculkan tombol Export & Reset setelah login berhasil
            self.btn_export.pack(side="left", padx=5, pady=10)
            self.btn_reset.pack(side="left", padx=5, pady=10)

            if action_type == "VIEW_LOGS":
                self.execute_admin_view_logs()
            elif action_type == "RESET_DB":
                self.execute_admin_reset()
        else:
            self.status_label.configure(text="⚠️ Access Denied: Incorrect Admin Password!", text_color="#ff3333")
            self.login_win.destroy()

    def execute_admin_view_logs(self):
        voters_list = db_get_voters()

        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")

        if voters_list:
            self.log_box.insert("0.0", f"--- SECURE HASH LOG ({len(voters_list)} Voters) ---\n")
            for idx, voter_hash in enumerate(voters_list, 1):
                short_hash = voter_hash[:16] + "..."
                self.log_box.insert("end", f"{idx}. Hash: {short_hash}\n")
        else:
            self.log_box.insert("0.0", "No data available. Database is empty.")

        self.log_box.configure(state="disabled")
        self.status_label.configure(text="✅ Secure logs loaded successfully!", text_color=self.color_accent)

    def execute_admin_export(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Document", "*.csv")],
            title="Save Audit Log As"
        )

        if not file_path:
            return

        try:
            results = db_get_results()
            voters = db_get_voters()

            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(["--- VOTING SYSTEM AUDIT REPORT ---"])
                writer.writerow(["Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow([])

                writer.writerow(["1. AGGREGATE RESULTS"])
                writer.writerow(["Candidate", "Total Votes"])
                for candidate, votes in results.items():
                    writer.writerow([candidate, votes])

                writer.writerow([])

                writer.writerow(["2. SECURE VOTER HASH LOG (SHA-256)"])
                writer.writerow(["No.", "Encrypted Voter ID"])
                for idx, v_hash in enumerate(voters, 1):
                    writer.writerow([idx, v_hash])

            self.status_label.configure(text=f"✅ Data successfully exported to CSV!", text_color=self.color_accent)
        except Exception as e:
            self.status_label.configure(text=f"⚠️ Export failed: {e}", text_color="#ff3333")

    def execute_admin_reset(self):
        db_reset_system()
        self.update_results()

        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.insert("0.0", "Database cleared. No logs to show.")
        self.log_box.configure(state="disabled")

        self.btn_export.pack_forget()
        self.btn_reset.pack_forget()
        self.is_admin_authenticated = False

        self.status_label.configure(text="🔄 Database Reset Successful!", text_color="#3399ff")


if __name__ == "__main__":
    VotingSystem().mainloop()

