import pygame, pyttsx3, random, math, speech_recognition as sr
from pygame.locals import *
from sys import exit
from datetime import datetime
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
fonte_log = pygame.font.SysFont("arial", 32)
fundo_menu = pygame.image.load('assets/fundo_menu.png')
fundo_game = pygame.image.load('assets/fundo_game.png')
fundo_morte = pygame.image.load('assets/fundo_morte.png')
runner = pygame.image.load('assets/runner.png')
enemy = pygame.image.load('assets/enemy.png')

# Sons

musica_game = pygame.mixer.Sound('assets/game.mp3')
botoes = pygame.mixer.Sound('assets/botoes.wav')
botoes.set_volume(0.5)
musica_game.set_volume(0.5)

# Log de tentativas
tentativas = []

# Função para pedir o nome do jogador
def pedir_nome():
    input_box = pygame.Rect(tela_x // 2 - 200, tela_y // 2, 400, 60)
    fonte_input = pygame.font.SysFont("arial", 48)
    nome = ""
    ativo = True

    while ativo:
        tela.blit(fundo_menu, (0, 0))
        prompt = fonte_input.render("Nome:", True, branco)
        tela.blit(prompt, (tela_x // 2 - prompt.get_width() // 2, tela_y // 2 - 80))
        pygame.draw.rect(tela, azul, input_box, 2)
        txt_surface = fonte_input.render(nome, True, branco)
        # Centraliza o texto na caixa de input
        text_x = input_box.x + (input_box.width - txt_surface.get_width()) // 2
        text_y = input_box.y + (input_box.height - txt_surface.get_height()) // 2
        tela.blit(txt_surface, (text_x, text_y))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    botoes.play()  # Toca o som ao apertar ENTER
                    ativo = False
                elif event.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if len(nome) < 20 and event.unicode.isprintable():
                        nome += event.unicode
    if nome.strip() == "":
        return "Unknown"
    return nome.strip()

def jogar(jogador):
    lanes = [75, 220, 370, 520, 665, 827]

    tamanho_runner = (100, 150)
    tamanho_enemy = (100, 150)

    posicao_runner = [tamanho[0] // 2, tamanho[1] - tamanho_runner[0]]

    inimigos = []  # Cada inimigo será [x, y, ultrapassou_flag]
    velocidade_enemy = 5

    enemy_spawn_time = random.randint(2000, 3000)
    ultimo_spawn = pygame.time.get_ticks()

    pontuacao = 0
    paused = False

    pause_blink = True
    pause_blink_timer = 0
    pause_blink_interval = 2000

    fundo_y = 0
    fundo_vel = 5

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
                    menu(jogador)
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
            inimigos.append([lane_x, 0, False])  # [x, y, ultrapassou_flag]
            ultimo_spawn = tempo_atual
            enemy_spawn_time = random.randint(2000, 3000)

        # Atualiza posição dos inimigos e conta ultrapassagens
        for inimigo in inimigos:
            inimigo[1] += velocidade_enemy
            # Conta ultrapassagem se o inimigo passou do runner e ainda não foi contado
            if not inimigo[2] and inimigo[1] > posicao_runner[1] + tamanho_runner[1]:
                pontuacao += 1
                inimigo[2] = True

        inimigos = [i for i in inimigos if i[1] < tela_y]

        # --- Colisão ---
        runner_rect = pygame.Rect(posicao_runner[0], posicao_runner[1], tamanho_runner[0], tamanho_runner[1])
        for inimigo in inimigos:
            enemy_rect = pygame.Rect(inimigo[0], inimigo[1], tamanho_enemy[0], tamanho_enemy[1])
            if runner_rect.colliderect(enemy_rect):
                musica_game.stop()
                # Salva tentativa no log
                tentativas.append({
                    "nome": jogador,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "pontuacao": pontuacao
                })
                if len(tentativas) > 5:
                    tentativas.pop(0)
                # Mostra a tela de game over com log
                mostrar_game_over(pontuacao, jogador)
                return  # Sai do jogo e volta ao menu

        # --- Desenho do jogo ---
        tela.blit(fundo_game, (0, fundo_y))
        tela.blit(fundo_game, (0, fundo_y - tela_y))

        tela.blit(runner, posicao_runner)
        for inimigo in inimigos:
            tela.blit(enemy, (inimigo[0], inimigo[1]))

        pygame.display.update()
        relogio.tick(60)

def mostrar_game_over(pontuacao, jogador):
    tela.blit(fundo_morte, (0, 0))
    fim_text = fonte.render("GAME OVER", True, vermelho)
    pontos_text = pygame.font.SysFont("arial", 60).render(f"Ultrapassagens: {pontuacao}", True, amarelo)
    tela.blit(fim_text, (tela_x // 2 - fim_text.get_width() // 2, 80))
    tela.blit(pontos_text, (tela_x // 2 - pontos_text.get_width() // 2, 220))

    # Log das últimas 5 tentativas
    y_log = 320
    log_title = fonte_log.render("Últimas 5 tentativas:", True, branco)
    tela.blit(log_title, (tela_x // 2 - log_title.get_width() // 2, y_log))
    y_log += 40

    for tentativa in tentativas[-5:][::-1]:
        log_text = fonte_log.render(
            f"{tentativa['data']} - {tentativa['nome']}: {tentativa['pontuacao']} pts",
            True, amarelo if tentativa['nome'] == jogador else branco
        )
        tela.blit(log_text, (tela_x // 2 - log_text.get_width() // 2, y_log))
        y_log += 36

    pygame.display.update()
    pygame.time.wait(3500)

def menu(jogador):
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
                    jogar(jogador)
                    return
                elif event.key == pygame.K_ESCAPE:
                    botoes.play()
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if botao_jogar.collidepoint(event.pos):
                    botoes.play()
                    jogar(jogador)
                    return
                elif botao_sair.collidepoint(event.pos):
                    botoes.play()
                    pygame.quit()
                    exit()

# --- INÍCIO DO JOGO ---
jogador_nome = pedir_nome()
menu(jogador_nome)