import pygame
import random

pygame.init()

PUTIH = (255, 255, 255)
KUNING = (255, 255, 102)
HITAM = (0, 0, 0)
MERAH = (213, 50, 80)
HIJAU = (0, 255, 0)

LEBAR = 600
TINGGI = 400
dis = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption('Snake Game - Score & Retry')

relo = pygame.time.Clock()
UKURAN_BLOK = 10
KECEPATAN = 15

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)


def tampilkan_skor(skor):
    value = score_font.render("Skor Anda: " + str(skor), True, KUNING)
    dis.blit(value, [0, 0])


def pesan_layar(msg, warna):
    mesg = font_style.render(msg, True, warna)
    dis.blit(mesg, [LEBAR / 6, TINGGI / 3])


def gameLoop():
    game_over = False
    game_close = False

    x1 = LEBAR / 2
    y1 = TINGGI / 2
    x1_change = 0
    y1_change = 0

    daftar_ular = []
    panjang_ular = 1

    makananx = round(random.randrange(0, LEBAR - UKURAN_BLOK) / 10.0) * 10.0
    makanany = round(random.randrange(0, TINGGI - UKURAN_BLOK) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(HITAM)
            pesan_layar("Kalah! Tekan C-Main Lagi atau Q-Keluar", MERAH)
            tampilkan_skor(panjang_ular - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -UKURAN_BLOK
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = UKURAN_BLOK
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -UKURAN_BLOK
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = UKURAN_BLOK
                    x1_change = 0

        if x1 >= LEBAR or x1 < 0 or y1 >= TINGGI or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(HITAM)

        pygame.draw.rect(dis, MERAH, [makananx, makanany, UKURAN_BLOK, UKURAN_BLOK])

        kepala_ular = [x1, y1]
        daftar_ular.append(kepala_ular)
        if len(daftar_ular) > panjang_ular:
            del daftar_ular[0]

        for x in daftar_ular[:-1]:
            if x == kepala_ular:
                game_close = True

        for blok in daftar_ular:
            pygame.draw.rect(dis, HIJAU, [blok[0], blok[1], UKURAN_BLOK, UKURAN_BLOK])

        tampilkan_skor(panjang_ular - 1)
        pygame.display.update()

        if x1 == makananx and y1 == makanany:
            makananx = round(random.randrange(0, LEBAR - UKURAN_BLOK) / 10.0) * 10.0
            makanany = round(random.randrange(0, TINGGI - UKURAN_BLOK) / 10.0) * 10.0
            panjang_ular += 1

        relo.tick(KECEPATAN)

    pygame.quit()
    quit()


gameLoop()