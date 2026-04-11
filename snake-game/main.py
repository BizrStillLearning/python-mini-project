import pygame
import random
import sys

WARNA = {
    "PUTIH": (255, 255, 255),
    "HITAM": (0, 0, 0),
    "MERAH": (213, 50, 80),
    "DARAH": (150, 0, 0),
    "HIJAU": (0, 255, 0),
    "KUNING": (255, 255, 102),
    "ABU_TUA": (40, 40, 40),
    "BG_TERANG": (170, 215, 81),
    "BG_GELAP": (162, 209, 73),
    "HEADER": (74, 117, 44),
    "TEMBOK": (43, 71, 26)
}

LEBAR, TINGGI_TOTAL = 600, 480
TINGGI_BAR = 80
UKURAN_BLOK = 20


class PartikelDarah:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.lifetime = 20

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, WARNA["MERAH"], (int(self.pos[0]), int(self.pos[1])), random.randint(2, 5))


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
        # Perbaikan Logika Tembok: Mati tepat di garis
        if kepala[0] >= LEBAR or kepala[0] < 0 or kepala[1] >= TINGGI_TOTAL or kepala[1] < TINGGI_BAR:
            return True
        if kepala in self.daftar_tubuh[:-1]:
            return True
        return False


class Makanan:
    def __init__(self):
        self.posisi = [0, 0]
        self.spawn()

    def spawn(self):
        self.posisi[0] = random.randrange(0, LEBAR, UKURAN_BLOK)
        self.posisi[1] = random.randrange(TINGGI_BAR, TINGGI_TOTAL, UKURAN_BLOK)


class GameSnake:
    def __init__(self):
        pygame.init()
        self.dis = pygame.display.set_mode((LEBAR, TINGGI_TOTAL))
        pygame.display.set_caption('Snake Game Pro - Informatics Edition')
        self.clock = pygame.time.Clock()
        self.font_skor = pygame.font.SysFont("bahnschrift", 30)
        self.font_tombol = pygame.font.SysFont("bahnschrift", 22)
        self.font_judul = pygame.font.SysFont("bahnschrift", 50)
        self.partikel = []

        try:
            self.img_apel = pygame.transform.scale(pygame.image.load("assets/apple.png").convert_alpha(),
                                                   (UKURAN_BLOK, UKURAN_BLOK))
            self.img_kepala = pygame.transform.scale(pygame.image.load("assets/head.png").convert_alpha(),
                                                     (UKURAN_BLOK, UKURAN_BLOK))
            self.img_badan = pygame.transform.scale(pygame.image.load("assets/body.png").convert_alpha(),
                                                    (UKURAN_BLOK, UKURAN_BLOK))
        except:
            print("Aset tidak ditemukan!")
            sys.exit()

        self.game_started = False
        self.reset_game()

    def reset_game(self):
        self.ular = Ular()
        self.makanan = Makanan()
        self.game_over = False
        self.game_close = False
        self.kecepatan = 10
        self.partikel = []

    def gambar_ui_statis(self):
        pygame.draw.rect(self.dis, WARNA["HEADER"], [0, 0, LEBAR, TINGGI_BAR])

        skor = self.font_skor.render(f"🍎 {self.ular.panjang - 1}", True, WARNA["PUTIH"])
        self.dis.blit(skor, [20, 25])

        info = self.font_tombol.render("SNAKE GAME V 1.0", True, WARNA["KUNING"])
        rect_info = info.get_rect(center=(LEBAR // 2, TINGGI_BAR // 2))
        self.dis.blit(info, rect_info)

    def gambar_tembok(self):
        pygame.draw.rect(self.dis, WARNA["TEMBOK"], [0, TINGGI_BAR, LEBAR, TINGGI_TOTAL - TINGGI_BAR], 4)

    def gambar_background_game(self):
        for x in range(0, LEBAR, UKURAN_BLOK):
            for y in range(TINGGI_BAR, TINGGI_TOTAL, UKURAN_BLOK):
                warna = WARNA["BG_TERANG"] if (x // UKURAN_BLOK + (y - TINGGI_BAR) // UKURAN_BLOK) % 2 == 0 else WARNA[
                    "BG_GELAP"]
                pygame.draw.rect(self.dis, warna, [x, y, UKURAN_BLOK, UKURAN_BLOK])

    def buat_percikan(self, x, y):
        for _ in range(20):
            self.partikel.append(PartikelDarah(x + UKURAN_BLOK // 2, y + UKURAN_BLOK // 2))

    def layar_awal(self):
        self.gambar_background_game()
        overlay = pygame.Surface((LEBAR, TINGGI_TOTAL))
        overlay.set_alpha(200);
        overlay.fill((0, 0, 0))
        self.dis.blit(overlay, (0, 0))
        judul = self.font_judul.render("SNAKE GAME", True, WARNA["HIJAU"])
        self.dis.blit(judul, judul.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 - 40)))

        pygame.draw.rect(self.dis, WARNA["HEADER"], [LEBAR / 2 - 110, TINGGI_TOTAL / 2 + 30, 220, 50], border_radius=10)
        txt = self.font_tombol.render("PRESS ENTER TO START", True, WARNA["PUTIH"])
        self.dis.blit(txt, txt.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 + 55)))
        pygame.display.update()

    def jalankan(self):
        while not self.game_over:
            while not self.game_started:
                self.layar_awal()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN: self.game_started = True
                        if event.key == pygame.K_q: pygame.quit(); sys.exit()
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            while self.game_close:
                self.gambar_background_game()
                for p in self.partikel: p.draw(self.dis)

                overlay = pygame.Surface((LEBAR, TINGGI_TOTAL), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.dis.blit(overlay, (0, 0))

                msg = self.font_skor.render("GAME OVER", True, WARNA["MERAH"])
                self.dis.blit(msg, msg.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 - 20)))
                instr = self.font_tombol.render("ENTER: RETRY | Q: QUIT", True, WARNA["PUTIH"])
                self.dis.blit(instr, instr.get_rect(center=(LEBAR / 2, TINGGI_TOTAL / 2 + 30)))
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q: pygame.quit(); sys.exit()
                        if event.key == pygame.K_RETURN: self.reset_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.ular.x_change == 0:
                        self.ular.x_change, self.ular.y_change = -UKURAN_BLOK, 0
                    elif event.key == pygame.K_RIGHT and self.ular.x_change == 0:
                        self.ular.x_change, self.ular.y_change = UKURAN_BLOK, 0
                    elif event.key == pygame.K_UP and self.ular.y_change == 0:
                        self.ular.y_change, self.ular.x_change = -UKURAN_BLOK, 0
                    elif event.key == pygame.K_DOWN and self.ular.y_change == 0:
                        self.ular.y_change, self.ular.x_change = UKURAN_BLOK, 0

            if self.ular.x_change != 0 or self.ular.y_change != 0:
                self.ular.perbarui_posisi()

            if self.ular.cek_tabrakan():
                self.buat_percikan(self.ular.daftar_tubuh[-1][0], self.ular.daftar_tubuh[-1][1])
                self.game_close = True

            if self.ular.daftar_tubuh[-1] == self.makanan.posisi:
                self.makanan.spawn()
                self.ular.panjang += 1
                self.kecepatan += 0.2

            self.gambar_background_game()
            for p in self.partikel:
                p.update()
                p.draw(self.dis)

            self.gambar_tembok()
            self.gambar_ui_statis()
            self.dis.blit(self.img_apel, (self.makanan.posisi[0], self.makanan.posisi[1]))
            for i, blok in enumerate(self.ular.daftar_tubuh):
                img = self.img_kepala if i == len(self.ular.daftar_tubuh) - 1 else self.img_badan
                self.dis.blit(img, (blok[0], blok[1]))

            pygame.display.update()
            self.clock.tick(self.kecepatan)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameSnake()
    game.jalankan()