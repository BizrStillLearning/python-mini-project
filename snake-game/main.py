import pygame
import random
import sys
import json
import os

WARNA = {
    "PUTIH": (255, 255, 255),
    "HITAM": (0, 0, 0),
    "MERAH": (213, 50, 80),
    "HIJAU": (0, 255, 0),
    "KUNING": (255, 255, 102),
    "EMAS": (255, 215, 0),
    "BIRU": (30, 144, 255),
    "ABU_TUA": (40, 40, 40),
    "BG_TERANG": (170, 215, 81),
    "BG_GELAP": (162, 209, 73),
    "HEADER": (74, 117, 44),
    "TEMBOK": (43, 71, 26)
}

LEBAR, TINGGI_TOTAL = 600, 480
TINGGI_BAR = 80
UKURAN_BLOK = 20
FILE_SCORE = "highscore.json"


def muat_highscore():
    if os.path.exists(FILE_SCORE):
        try:
            with open(FILE_SCORE, "r") as f:
                return json.load(f).get("highscore", 0)
        except:
            return 0
    return 0


def simpan_highscore(skor):
    with open(FILE_SCORE, "w") as f:
        json.dump({"highscore": skor}, f)


class Partikel:
    def __init__(self, x, y, warna):
        self.pos = [x, y]
        self.vel = [random.uniform(-4, 4), random.uniform(-4, 4)]
        self.lifetime = random.randint(10, 20)
        self.warna = warna

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            s = pygame.Surface((4, 4))
            s.set_alpha(self.lifetime * 12)
            s.fill(self.warna)
            surface.blit(s, (int(self.pos[0]), int(self.pos[1])))


class Ular:
    def __init__(self):
        self.panjang = 1
        self.daftar_tubuh = [[LEBAR // 2, TINGGI_BAR + 200]]
        self.x_change = 0
        self.y_change = 0

    def perbarui_posisi(self):
        kepala = [self.daftar_tubuh[-1][0] + self.x_change,
                  self.daftar_tubuh[-1][1] + self.y_change]
        self.daftar_tubuh.append(kepala)
        if len(self.daftar_tubuh) > self.panjang:
            del self.daftar_tubuh[0]

    def cek_tabrakan(self):
        kepala = self.daftar_tubuh[-1]
        if kepala[0] >= LEBAR or kepala[0] < 0 or kepala[1] >= TINGGI_TOTAL or kepala[1] < TINGGI_BAR:
            return True
        if kepala in self.daftar_tubuh[:-1]:
            return True
        return False


class Makanan:
    def __init__(self, tipe="normal"):
        self.posisi = [0, 0]
        self.tipe = tipe
        self.spawn()

    def spawn(self):
        self.posisi[0] = random.randrange(0, LEBAR, UKURAN_BLOK)
        self.posisi[1] = random.randrange(TINGGI_BAR, TINGGI_TOTAL, UKURAN_BLOK)


class GameSnake:
    def __init__(self):
        pygame.init()
        self.dis = pygame.display.set_mode((LEBAR, TINGGI_TOTAL))
        pygame.display.set_caption('Snake Game V 1.0 - Python Mini Game')
        self.clock = pygame.time.Clock()
        self.font_skor = pygame.font.SysFont("bahnschrift", 25)
        self.font_tombol = pygame.font.SysFont("bahnschrift", 22)
        self.font_judul = pygame.font.SysFont("bahnschrift", 50)

        self.partikel = []
        self.shake_amount = 0
        self.highscore = muat_highscore()

        try:
            self.img_apel = pygame.transform.scale(pygame.image.load("assets/apple.png").convert_alpha(),
                                                   (UKURAN_BLOK, UKURAN_BLOK))
            self.img_kepala = pygame.transform.scale(pygame.image.load("assets/head.png").convert_alpha(),
                                                     (UKURAN_BLOK, UKURAN_BLOK))
            self.img_badan = pygame.transform.scale(pygame.image.load("assets/body.png").convert_alpha(),
                                                    (UKURAN_BLOK, UKURAN_BLOK))
        except:
            self.img_apel = self.img_kepala = self.img_badan = None

        self.game_started = False
        self.reset_game()

    def reset_game(self):
        self.ular = Ular()
        self.makanan = Makanan("normal")
        self.game_over = False
        self.game_close = False
        self.kecepatan = 10
        self.skor_saat_ini = 0
        self.partikel = []
        self.shake_amount = 0

    def buat_efek(self, x, y, warna, jumlah=15):
        for _ in range(jumlah):
            self.partikel.append(Partikel(x, y, warna))

    def gambar_ui(self):
        pygame.draw.rect(self.dis, WARNA["HEADER"], [0, 0, LEBAR, TINGGI_BAR])
        skor_txt = self.font_skor.render(f"SCORE: {self.skor_saat_ini}", True, WARNA["PUTIH"])
        self.dis.blit(skor_txt, [30, 25])

        info = self.font_tombol.render("SNAKE GAME V 1.0", True, WARNA["KUNING"])
        self.dis.blit(info, info.get_rect(center=(LEBAR // 2, TINGGI_BAR // 2)))

        skor_hi = self.font_skor.render(f"🏆 BEST: {self.highscore}", True, WARNA["KUNING"])
        self.dis.blit(skor_hi, [LEBAR - 170, 25])

    def gambar_background_game(self, ox, oy):
        for x in range(0, LEBAR, UKURAN_BLOK):
            for y in range(TINGGI_BAR, TINGGI_TOTAL, UKURAN_BLOK):
                warna = WARNA["BG_TERANG"] if (x // UKURAN_BLOK + (y - TINGGI_BAR) // UKURAN_BLOK) % 2 == 0 else WARNA[
                    "BG_GELAP"]
                pygame.draw.rect(self.dis, warna, [x + ox, y + oy, UKURAN_BLOK, UKURAN_BLOK])

    def jalankan(self):
        while not self.game_over:
            while not self.game_started:
                self.dis.fill(WARNA["HITAM"])
                self.gambar_background_game(0, 0)
                overlay = pygame.Surface((LEBAR, TINGGI_TOTAL));
                overlay.set_alpha(180)
                self.dis.blit(overlay, (0, 0))
                txt = self.font_judul.render("SNAKE ADVENTURE", True, WARNA["HIJAU"])
                self.dis.blit(txt, txt.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 - 20)))
                instr = self.font_tombol.render("PRESS ENTER TO START", True, WARNA["PUTIH"])
                self.dis.blit(instr, instr.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 + 40)))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: self.game_started = True
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            while self.game_close:
                if self.skor_saat_ini > self.highscore:
                    self.highscore = self.skor_saat_ini
                    simpan_highscore(self.highscore)

                overlay = pygame.Surface((LEBAR, TINGGI_TOTAL), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.dis.blit(overlay, (0, 0))

                msg = self.font_skor.render("GAME OVER", True, WARNA["MERAH"])
                self.dis.blit(msg, msg.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 - 30)))
                final_skr = self.font_tombol.render(f"Score: {self.skor_saat_ini} | High: {self.highscore}", True,
                                                    WARNA["KUNING"])
                self.dis.blit(final_skr, final_skr.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 + 10)))
                instr = self.font_tombol.render("ENTER: RETRY | Q: QUIT", True, WARNA["PUTIH"])
                self.dis.blit(instr, instr.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 + 50)))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q: pygame.quit(); sys.exit()
                        if event.key == pygame.K_RETURN: self.reset_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.game_over = True
                if event.type == pygame.KEYDOWN:
                    # LOGIKA KONTROL YANG TELAH DIPERBAIKI
                    if event.key == pygame.K_LEFT and self.ular.x_change == 0:
                        self.ular.x_change = -UKURAN_BLOK
                        self.ular.y_change = 0
                    elif event.key == pygame.K_RIGHT and self.ular.x_change == 0:
                        self.ular.x_change = UKURAN_BLOK
                        self.ular.y_change = 0
                    elif event.key == pygame.K_UP and self.ular.y_change == 0:
                        self.ular.y_change = -UKURAN_BLOK
                        self.ular.x_change = 0
                    elif event.key == pygame.K_DOWN and self.ular.y_change == 0:
                        self.ular.y_change = UKURAN_BLOK
                        self.ular.x_change = 0

            if self.ular.x_change != 0 or self.ular.y_change != 0:
                self.ular.perbarui_posisi()

            if self.ular.cek_tabrakan():
                self.shake_amount = 15
                self.buat_efek(self.ular.daftar_tubuh[-1][0], self.ular.daftar_tubuh[-1][1], WARNA["MERAH"], 30)
                self.game_close = True

            if self.ular.daftar_tubuh[-1] == self.makanan.posisi:
                if self.makanan.tipe == "emas":
                    self.skor_saat_ini += 5
                    self.shake_amount = 8
                    self.buat_efek(self.makanan.posisi[0], self.makanan.posisi[1], WARNA["EMAS"], 25)
                elif self.makanan.tipe == "shrink":
                    self.skor_saat_ini += 1
                    if self.ular.panjang > 1: self.ular.panjang -= 1
                    self.buat_efek(self.makanan.posisi[0], self.makanan.posisi[1], WARNA["BIRU"], 20)
                else:
                    self.skor_saat_ini += 1
                    self.ular.panjang += 1
                    self.buat_efek(self.makanan.posisi[0], self.makanan.posisi[1], WARNA["PUTIH"], 10)

                rand = random.random()
                tipe = "emas" if rand < 0.15 else "shrink" if rand < 0.3 else "normal"
                self.makanan = Makanan(tipe)
                self.kecepatan += 0.2

            ox = random.randint(-self.shake_amount, self.shake_amount)
            oy = random.randint(-self.shake_amount, self.shake_amount)
            if self.shake_amount > 0: self.shake_amount -= 1

            # RENDERING
            self.gambar_background_game(ox, oy)
            for p in self.partikel:
                p.update();
                p.draw(self.dis)

            mx, my = self.makanan.posisi[0] + ox, self.makanan.posisi[1] + oy
            if self.makanan.tipe == "emas":
                pygame.draw.circle(self.dis, WARNA["EMAS"], (mx + 10, my + 10), 12)
                pygame.draw.circle(self.dis, WARNA["KUNING"], (mx + 10, my + 10), 8)
            elif self.makanan.tipe == "shrink":
                pygame.draw.rect(self.dis, WARNA["BIRU"], [mx, my, UKURAN_BLOK, UKURAN_BLOK], border_radius=5)
            else:
                if self.img_apel:
                    self.dis.blit(self.img_apel, (mx, my))
                else:
                    pygame.draw.rect(self.dis, WARNA["MERAH"], [mx, my, UKURAN_BLOK, UKURAN_BLOK])

            for i, blok in enumerate(self.ular.daftar_tubuh):
                bx, by = blok[0] + ox, blok[1] + oy
                if i == len(self.ular.daftar_tubuh) - 1:
                    if self.img_kepala:
                        self.dis.blit(self.img_kepala, (bx, by))
                    else:
                        pygame.draw.rect(self.dis, (0, 200, 0), [bx, by, UKURAN_BLOK, UKURAN_BLOK])
                else:
                    if self.img_badan:
                        self.dis.blit(self.img_badan, (bx, by))
                    else:
                        pygame.draw.rect(self.dis, (0, 150, 0), [bx, by, UKURAN_BLOK, UKURAN_BLOK])

            self.gambar_ui()
            pygame.display.update()
            self.clock.tick(self.kecepatan)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GameSnake().jalankan()