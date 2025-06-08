import pygame, pyttsx3, random, math, speech_recognition as sr
from pygame.locals import *
from sys import exit
from resources.recs import inicializarBancoDeDados, escreverDados, limpa_tela, aguarde


# variaveis

pygame.init()
inicializarBancoDeDados()
tela_x = 1000
tela_y = 700
tamanho = (tela_x, tela_y)
relogio = pygame.time.Clock()
tela = pygame.display.set_mode(tamanho)
icone = pygame.image.load('assets/icone.png')
pygame.display.set_icon(icone)
pygame.display.set_caption("MidNightRunner")

# Cores

preto = (0, 0, 0)
branco = (255, 255, 255)
ciano = (0, 255, 255)
rosa = (255, 0, 255)
verde = (0, 255, 0)
vermelho = (255, 0, 0)
azul = (0, 0, 255)
amarelo = (255, 255, 0)

# Fontes

fonte = pygame.font.SysFont("arial",120)
fundo_menu = pygame.image.load('assets/fundo_menu.png')
fundo_game = pygame.image.load('assets/fundo_game.png')
runner = pygame.image.load('assets/runner.png')
enemy = pygame.image.load('assets/enemy.png')

# Sons

musica_game = pygame.mixer.Sound('assets/game.mp3')
botoes = pygame.mixer.Sound('assets/botoes.wav')
botoes.set_volume(0.5)
musica_game.set_volume(0.5)

def reconhecer_pontuacao():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="pt-BR")
        return texto
    except:
        return ""
    
def jogar():
    lanes = [75, 220, 370, 520, 665, 827]

    tamanho_runner = (100, 150)
    tamanho_enemy = (100, 150)

    posicao_runner = [tamanho[0] // 2, tamanho[1] - tamanho_runner[0]]

    inimigos = []

    velocidade_enemy = 5
    pontuacao = 0

    enemy_spawn_time = random.randint(2000, 3000)
    ultimo_spawn = pygame.time.get_ticks()

    pontos = 0
    velocidade = 5
    difficulty = 30
    paused = False
    frame = 0

    pause_blink = True
    pause_blink_timer = 0
    pause_blink_interval = 2000

    # Variáveis para o fundo
    fundo_y = 0
    fundo_vel = 5  # velocidade do fundo

    # Toca a música do jogo em loop
    musica_game.play(-1)

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                musica_game.stop()
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    musica_game.stop()
                    botoes.play()
                    menu()
                    return
                elif evento.key == pygame.K_ESCAPE:
                    paused = not paused
                    pause_blink = True
                    pause_blink_timer = pygame.time.get_ticks()

        if not paused:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT] and posicao_runner[0] > 57:
                posicao_runner[0] -= 10
            if teclas[pygame.K_RIGHT] and posicao_runner[0] < 942 - tamanho_runner[0]:
                posicao_runner[0] += 10

            # Atualiza o fundo
            fundo_y += fundo_vel
            if fundo_y >= tela_y:
                fundo_y = 0

        if paused:
            tela.blit(fundo_game, (0, 0))
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - pause_blink_timer >= pause_blink_interval:
                pause_blink = not pause_blink
                pause_blink_timer = tempo_atual
            if pause_blink:
                pause_text = fonte.render("PAUSE", True, amarelo)
                text_rect = pause_text.get_rect(center=(tela_x // 2, tela_y // 2))
                tela.blit(pause_text, text_rect)
            pygame.display.update()
            relogio.tick(60)
            continue

        # Spawn de inimigos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_spawn >= enemy_spawn_time:
            lane_x = random.choice(lanes)
            inimigos.append([lane_x, 0])
            ultimo_spawn = tempo_atual
            enemy_spawn_time = random.randint(2000, 3000)

        # Atualiza posição dos inimigos
        for inimigo in inimigos:
            inimigo[1] += velocidade_enemy

        inimigos = [i for i in inimigos if i[1] < tela_y]

        # --- Colisão ---
        runner_rect = pygame.Rect(posicao_runner[0], posicao_runner[1], tamanho_runner[0], tamanho_runner[1])
        for inimigo in inimigos:
            enemy_rect = pygame.Rect(inimigo[0], inimigo[1], tamanho_enemy[0], tamanho_enemy[1])
            if runner_rect.colliderect(enemy_rect):
                musica_game.stop()
                # Opcional: mostrar mensagem de fim de jogo
                # fim_text = fonte.render("GAME OVER", True, vermelho)
                # tela.blit(fim_text, (tela_x // 2 - 250, tela_y // 2 - 60))
                # pygame.display.update()
                # pygame.time.wait(2000)
                return  # Sai do jogo e volta ao menu

        # --- Desenho do jogo ---
        # Fundo em loop
        tela.blit(fundo_game, (0, fundo_y))
        tela.blit(fundo_game, (0, fundo_y - tela_y))

        tela.blit(runner, posicao_runner)
        for inimigo in inimigos:
            tela.blit(enemy, inimigo)

        pygame.display.update()
        relogio.tick(60)

def menu():
    botao_jogar = pygame.Rect(tela_x // 2 - 150, tela_y // 2 - 60, 300, 80)
    botao_sair = pygame.Rect(tela_x // 2 - 150, tela_y // 2 + 40, 300, 80)
    fonte_botao = pygame.font.SysFont("arial", 60)

    while True:
        tela.blit(fundo_menu, (0, 0))

        # Desenha botões
        pygame.draw.rect(tela, ciano, botao_jogar)
        pygame.draw.rect(tela, rosa, botao_sair)

        texto_jogar = fonte_botao.render("JOGAR", True, branco)
        texto_sair = fonte_botao.render("SAIR", True, branco)
        tela.blit(texto_jogar, (botao_jogar.x + 50, botao_jogar.y + 10))
        tela.blit(texto_sair, (botao_sair.x + 80, botao_sair.y + 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    botoes.play()
                    jogar()
                    return
                elif event.key == pygame.K_ESCAPE:
                    botoes.play()
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if botao_jogar.collidepoint(event.pos):
                    botoes.play()
                    jogar()
                    return
                elif botao_sair.collidepoint(event.pos):
                    botoes.play()
                    pygame.quit()
                    exit()

menu()



