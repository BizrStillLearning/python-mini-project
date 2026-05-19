import customtkinter as ctk
import sqlite3
import os

DB_FILE = "voting_system.db"

class VotingSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Voting System V 2.1 - Admin Audit")
        self.geometry("650x850")
        self.resizable(False, False)

        self.admin_password = "admin123"
        self.color_accent = "#33ff33"

        self.init_database()

        ctk.set_appearance_mode("dark")
        self.setup_ui()
        self.update_results()

    def init_database(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                name TEXT PRIMARY KEY,
                votes INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voters (
                voter_id TEXT PRIMARY KEY
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM candidates")
        if cursor.fetchone()[0] == 0:
            initial_data = [("Python", 0), ("JavaScript", 0), ("Golang", 0), ("C++", 0)]
            cursor.execSubmitedmany = cursor.executemany("INSERT INTO candidates VALUES (?, ?)", initial_data)
        conn.commit()
        conn.close()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, border_width=2, border_color=self.color_accent)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.main_frame, text="VOTE YOUR LANGUAGE",
                     font=("Bahnschrift", 28, "bold"), text_color=self.color_accent).pack(pady=15)

        self.id_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.id_frame.pack(pady=10)
        ctk.CTkLabel(self.id_frame, text="Enter Voter ID (NIM):", font=("Bahnschrift", 14)).pack(side="left", padx=10)
        self.entry_voter_id = ctk.CTkEntry(self.id_frame, placeholder_text="ID / NIM Number", width=180)
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

        self.status_label = ctk.CTkLabel(self.main_frame, text="Please enter your ID and cast your vote!",
                                         font=("Bahnschrift", 14), text_color="gray")
        self.status_label.pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="--- Admin Audit Log ---", font=("Bahnschrift", 12), text_color="gray").pack(pady=(10,0))
        self.log_box = ctk.CTkTextbox(self.main_frame, width=400, height=100, font=("Consolas", 12))
        self.log_box.pack(pady=5)
        self.log_box.insert("0.0", "Lock icon. Authenticate as admin to view voter logs.")
        self.log_box.configure(state="disabled")

        self.admin_btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.admin_btn_frame.pack(pady=10, side="bottom")

        self.btn_view_log = ctk.CTkButton(self.admin_btn_frame, text="🔐 View Logs", fg_color="#3b3b3b", command=self.admin_view_logs)
        self.btn_view_log.pack(side="left", padx=5)

        self.btn_reset = ctk.CTkButton(self.admin_btn_frame, text="🗑️ Reset DB", fg_color="#ff3333", text_color="black", font=("Bahnschrift", 14, "bold"), command=self.admin_reset)
        self.btn_reset.pack(side="left", padx=5)

    def cast_vote(self, lang):
        voter_id = self.entry_voter_id.get().strip()
        if not voter_id:
            self.status_label.configure(text="⚠️ Error: Please enter your Voter ID first!", text_color="#ffcc00")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters WHERE voter_id = ?", (voter_id,))
        if cursor.fetchone() is not None:
            self.status_label.configure(text=f"❌ ID '{voter_id}' has already voted!", text_color="#ff3333")
            conn.close()
            return

        try:
            cursor.execute("INSERT INTO voters VALUES (?)", (voter_id,))
            cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE name = ?", (lang,))
            conn.commit()
            self.status_label.configure(text=f"✅ Vote successfully cast for {lang}!", text_color=self.color_accent)
            self.entry_voter_id.delete(0, 'end')
        except sqlite3.Error as e:
            self.status_label.configure(text=f"⚠️ Database Error: {e}", text_color="#ff3333")
        finally:
            conn.close()

        self.update_results()

    def update_results(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, votes FROM candidates")
        data = dict(cursor.fetchall())
        total_votes = sum(data.values())

        for lang, count in data.items():
            if lang in self.result_labels:
                self.result_labels[lang].configure(text=f"{lang}: {count}")
                percentage = count / total_votes if total_votes > 0 else 0
                self.result_bars[lang].set(percentage)
        conn.close()

    def admin_view_logs(self):
        dialog = ctk.CTkInputDialog(text="Enter Admin Password to View Logs:", title="Admin Authentication")
        input_password = dialog.get_input()

        if input_password == self.admin_password:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Mengambil daftar ID dari tabel voters (Data Query)
            cursor.execute("SELECT voter_id FROM voters")
            voters_list = cursor.fetchall()
            conn.close()

            self.log_box.configure(state="normal")
            self.log_box.delete("0.0", "end")

            if voters_list:
                self.log_box.insert("0.0", f"--- TOTAL VOTERS LOG ({len(voters_list)}) ---\n")
                for idx, voter in enumerate(voters_list, 1):
                    self.log_box.insert("end", f"{idx}. Voter ID: {voter[0]}\n")
            else:
                self.log_box.insert("0.0", "No data available. Database is empty.")

            self.log_box.configure(state="disabled")
            self.status_label.configure(text="✅ Logs loaded successfully!", text_color=self.color_accent)
        elif input_password is None:
            pass
        else:
            self.status_label.configure(text="⚠️ Wrong Admin Password!", text_color="#ff3333")

    def admin_reset(self):
        dialog = ctk.CTkInputDialog(text="Enter Admin Password to Reset System:", title="Admin Authentication")
        input_password = dialog.get_input()

        if input_password == self.admin_password:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE candidates SET votes = 0")
            cursor.execute("DELETE FROM voters")
            conn.commit()
            conn.close()

            self.update_results()

            self.log_box.configure(state="normal")
            self.log_box.delete("0.0", "end")
            self.log_box.insert("0.0", "Database cleared. No logs to show.")
            self.log_box.configure(state="disabled")

            self.status_label.configure(text="🔄 Database Reset Successful!", text_color="#3399ff")
        elif input_password is None:
            pass
        else:
            self.status_label.configure(text="⚠️ Wrong Admin Password!", text_color="#ff3333")

if __name__ == "__main__":
    app = VotingSystem()
    app.mainloop()