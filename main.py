import pygame, pyttsx3, random, math, speech_recognition as sr, sys, aifc, json
from pygame.locals import *
from sys import exit
from datetime import datetime
from Recursos.recs import inicializarBancoDeDados, escreverDados, limpa_tela, aguarde

limpa_tela()
aguarde(1)

pygame.init()
inicializarBancoDeDados()

tela_x = 1000
tela_y = 700
tamanho = (tela_x, tela_y)
relogio = pygame.time.Clock()
tela = pygame.display.set_mode(tamanho)
icone = pygame.image.load('Recursos/assets/icone.png')
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
fundo_menu = pygame.image.load('Recursos/assets/fundo_menu.png')
fundo_game = pygame.image.load('Recursos/assets/fundo_game.png')
fundo_morte = pygame.image.load('Recursos/assets/fundo_morte.png')
runner = pygame.image.load('Recursos/assets/runner.png')
enemy = pygame.image.load('Recursos/assets/enemy.png')

# Sons
musica_game = pygame.mixer.Sound('Recursos/assets/game.mp3')
musica_pause = pygame.mixer.Sound('Recursos/assets/musica_pause.mp3')
botoes = pygame.mixer.Sound('Recursos/assets/botoes.wav')
botoes.set_volume(0.5)
musica_game.set_volume(0.5)
musica_pause.set_volume(0.5)

# Log de tentativas
tentativas = []
try:
    with open("log.dat", "r") as f:
        dados = f.read()
        if dados.strip():
            dadosDict = json.loads(dados)
            for nome, (pontuacao, data) in dadosDict.items():
                tentativas.append({
                    "nome": nome,
                    "pontuacao": int(pontuacao),
                    "data": data
                })
except Exception:
    tentativas = []

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
                    botoes.play()
                    ativo = False
                elif event.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    if len(nome) < 20 and event.unicode.isprintable():
                        nome += event.unicode
    if nome.strip() == "":
        return "Unknown"
    return nome.strip()

def reconhecer_lets_race():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga: Let's Race")
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="en-US")
        return texto
    except:
        return ""

def jogar(jogador):    
    lanes = [75, 220, 370, 520, 665, 827]
    tamanho_runner = (100, 150)
    tamanho_enemy = (100, 150)
    posicao_runner = [tela_x // 2, tela_y - tamanho_runner[1]]
    inimigos = []
    velocidade_enemy_inicial = 5
    velocidade_enemy = velocidade_enemy_inicial
    aumento_velocidade_intervalo = 10000  # 10 segundos
    ultimo_aumento_velocidade = pygame.time.get_ticks()
    min_spawn = 400
    max_spawn = 900
    enemy_spawn_time = random.randint(min_spawn, max_spawn)
    ultimo_spawn = pygame.time.get_ticks()
    pontuacao = 0
    paused = False
    pause_blink = True
    pause_blink_timer = 0
    pause_blink_interval = 1000
    fundo_y = 0
    fundo_vel_inicial = 5
    fundo_vel = fundo_vel_inicial
    musica_game.play(-1)
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
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
            if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and posicao_runner[0] > 57:
                posicao_runner[0] -= 10
            if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and posicao_runner[0] < 942 - tamanho_runner[0]:
                posicao_runner[0] += 10

            fundo_y += fundo_vel
            if fundo_y >= tela_y:
                fundo_y = 0

        if paused:
            musica_game.stop()
            if not pygame.mixer.get_busy():
                musica_pause.play(-1)
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
        else:
            musica_pause.stop()
            if not pygame.mixer.get_busy():
                musica_game.play(-1)

        # Aumenta a velocidade dos inimigos e do fundo a cada 10 segundos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_aumento_velocidade >= aumento_velocidade_intervalo:
            if velocidade_enemy < velocidade_enemy_inicial * 3:
                velocidade_enemy += 1
                fundo_vel = fundo_vel_inicial * (velocidade_enemy / velocidade_enemy_inicial)

                # Diminui o tempo de spawn conforme a velocidade aumenta

                min_spawn = max(200, min_spawn - 100)
                max_spawn = max(400, max_spawn - 150)
            ultimo_aumento_velocidade = tempo_atual

        # Spawn de inimigos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_spawn >= enemy_spawn_time:
            lanes_ocupadas = [inimigo[0] for inimigo in inimigos if inimigo[1] < tamanho_enemy[1]]
            lanes_disponiveis = [lane for lane in lanes if lane not in lanes_ocupadas]
            if lanes_disponiveis:
                lane_x = random.choice(lanes_disponiveis)
                inimigos.append([lane_x, -tamanho_enemy[1], False])  # [x, y, ultrapassou_flag]
                ultimo_spawn = tempo_atual
                enemy_spawn_time = random.randint(min_spawn, max_spawn)

        # Atualiza posição dos inimigos e conta ultrapassagens
        for inimigo in inimigos:
            inimigo[1] += velocidade_enemy
            # Conta ultrapassagem se a BASE do inimigo passou da BASE do runner e ainda não foi contado
            if not inimigo[2] and (inimigo[1] + tamanho_enemy[1]) > (posicao_runner[1] + tamanho_runner[1]):
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
                escreverDados(jogador, pontuacao)
                tentativas.append({
                    "nome": jogador,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "pontuacao": pontuacao
                })
                if len(tentativas) > 5:
                    tentativas.pop(0)
                mostrar_game_over(pontuacao, jogador)
                menu(jogador)
                return

        # --- Desenho do jogo ---
        tela.blit(fundo_game, (0, fundo_y))
        tela.blit(fundo_game, (0, fundo_y - tela_y))
        tela.blit(runner, posicao_runner)
        for inimigo in inimigos:
            tela.blit(enemy, (inimigo[0], inimigo[1]))

        
        # Fundo escuro e transparente centralizado no topo
        score_width, score_height = 240, 48
        score_x = (tela_x - score_width) // 2
        score_y = 20
        s = pygame.Surface((score_width, score_height))
        s.set_alpha(180)  # Transparência (0-255)
        s.fill((0, 0, 0))  # Preto
        tela.blit(s, (score_x, score_y))

        # Texto da pontuação centralizado (fonte menor)
        fonte_score = pygame.font.SysFont("arial", 28)
        score_text = fonte_score.render(f"Ultrapassagens: {pontuacao}", True, branco)
        text_rect = score_text.get_rect(center=(tela_x // 2, score_y + score_height // 2))
        tela.blit(score_text, text_rect)

        # --- Exibe comandos no canto superior esquerdo ---
        comandos_width, comandos_height = 220, 48
        comandos_x, comandos_y = 20, 20
        s_comandos = pygame.Surface((comandos_width, comandos_height))
        s_comandos.set_alpha(180)
        s_comandos.fill((0, 0, 0))
        tela.blit(s_comandos, (comandos_x, comandos_y))

        fonte_comandos = pygame.font.SysFont("arial", 20)
        texto1 = fonte_comandos.render("A/D ←/→: Movimento", True, branco)
        texto2 = fonte_comandos.render("ESC: Pause", True, branco)
        tela.blit(texto1, (comandos_x + 10, comandos_y + 5))
        tela.blit(texto2, (comandos_x + 10, comandos_y + 25))

        # --- Ícone animado no canto superior direito ---
        
        tempo_anim = pygame.time.get_ticks() // 200  # velocidade da animação
        pulsar = 1 + 0.15 * math.sin(pygame.time.get_ticks() / 300)  # efeito de pulsar
        invert_x = tempo_anim % 2 == 0
        invert_y = (tempo_anim // 2) % 2 == 0

        # Carrega e transforma o ícone
        icone_img = pygame.image.load('Recursos/assets/icone.png').convert_alpha()
        icone_base_size = 64  # tamanho base do ícone
        icone_size = int(icone_base_size * pulsar)
        icone_img = pygame.transform.scale(icone_img, (icone_size, icone_size))
        if invert_x:
            icone_img = pygame.transform.flip(icone_img, True, False)
        if invert_y:
            icone_img = pygame.transform.flip(icone_img, False, True)

        # Posição no canto superior direito
        icone_x = tela_x - icone_size - 20
        icone_y = 20
        tela.blit(icone_img, (icone_x, icone_y))

        pygame.display.update()
        relogio.tick(60)

def mostrar_game_over(pontuacao, jogador):
    tela.blit(fundo_morte, (0, 0))
    fim_text = fonte.render("GAME OVER", True, vermelho)
    pontos_text = pygame.font.SysFont("arial", 30).render(f"Pontos: {pontuacao}", True, branco)
    tela.blit(fim_text, (tela_x // 2 - fim_text.get_width() // 2, 80))
    tela.blit(pontos_text, (tela_x // 2 - pontos_text.get_width() // 2, 220))

    # Área do log (fundo preto semi-transparente)
    log_width = 600
    log_height = 260
    log_x = tela_x // 2 - log_width // 2
    log_y = 320
    log_rect = pygame.Rect(log_x, log_y, log_width, log_height)
    s = pygame.Surface((log_width, log_height))
    s.set_alpha(200)
    s.fill(preto)
    tela.blit(s, (log_x, log_y))

    # Título do log
    log_title = fonte_log.render("Últimas 5 tentativas:", True, branco)
    tela.blit(log_title, (tela_x // 2 - log_title.get_width() // 2, log_y + 10))

    # Lista das tentativas
    y_log = log_y + 50
    for tentativa in tentativas[-5:][::-1]:
        log_text = fonte_log.render(
            f"{tentativa['data']} - {tentativa['nome']}: {tentativa['pontuacao']} pts",
            True, amarelo if tentativa['nome'] == jogador else branco
        )
        tela.blit(log_text, (tela_x // 2 - log_text.get_width() // 2, y_log))
        y_log += 36

    # Botão "Menu"
    botao_menu = pygame.Rect(tela_x - 210, tela_y - 80, 180, 60)
    pygame.draw.rect(tela, amarelo, botao_menu)
    texto_menu = fonte_log.render("MENU", True, branco)
    tela.blit(texto_menu, (botao_menu.x + (botao_menu.width - texto_menu.get_width()) // 2,
                           botao_menu.y + (botao_menu.height - texto_menu.get_height()) // 2))

    pygame.display.update()

    # Fala a pontuação usando pyttsx3 (após exibir a tela)
    engine = pyttsx3.init()
    engine.say(f"Sua pontuação foi {pontuacao}")
    engine.runAndWait()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    botoes.play()
                    esperando = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if botao_menu.collidepoint(event.pos):
                    botoes.play()
                    esperando = False
        relogio.tick(60)

def menu(jogador):
    botao_jogar = pygame.Rect(tela_x // 2 - 150, tela_y // 2 - 60, 300, 80)
    botao_sair = pygame.Rect(tela_x // 2 - 150, tela_y // 2 + 40, 300, 80)
    fonte_botao = pygame.font.SysFont("arial", 60)

    while True:
        tela.blit(fundo_menu, (0, 0))
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
                    tela_historinha_controles()
                    jogar(jogador)
                    return
                elif event.key == pygame.K_ESCAPE:
                    botoes.play()
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if botao_jogar.collidepoint(event.pos):
                    botoes.play()
                    tela_historinha_controles()
                    jogar(jogador)
                    return
                elif botao_sair.collidepoint(event.pos):
                    botoes.play()
                    pygame.quit()
                    exit()

def tela_historinha_controles():
    while True:
        tela.blit(fundo_menu, (0, 0))
        # --- Caixa escura e transparente MAIOR ---
        box_width, box_height = 700, 400 
        box_x = (tela_x - box_width) // 2
        box_y = (tela_y - box_height) // 2
        s_box = pygame.Surface((box_width, box_height))
        s_box.set_alpha(200)
        s_box.fill((0, 0, 0))
        tela.blit(s_box, (box_x, box_y))

        # --- Texto da historinha ---
        fonte_hist = pygame.font.SysFont("arial", 28)
        hist1 = "Um corredor solitário que, após um dia de trabalho,"
        hist2 = "resolve dar um rolê de carro pra pensar um pouco."
        tela.blit(fonte_hist.render(hist1, True, branco), (box_x + 30, box_y + 40))
        tela.blit(fonte_hist.render(hist2, True, branco), (box_x + 30, box_y + 80))

        # --- Controles ---
        fonte_ctrl = pygame.font.SysFont("arial", 24)
        tela.blit(fonte_ctrl.render("Controles:", True, amarelo), (box_x + 30, box_y + 150))
        tela.blit(fonte_ctrl.render("A / ←  : Mover para a esquerda", True, branco), (box_x + 50, box_y + 190))
        tela.blit(fonte_ctrl.render("D / →  : Mover para a direita", True, branco), (box_x + 50, box_y + 230))
        tela.blit(fonte_ctrl.render("Espaço: Pausar/Continuar", True, branco), (box_x + 50, box_y + 270))

        # --- Mensagem para falar ---
        aviso = fonte_log.render("Diga: Let's Race para começar!", True, amarelo)
        tela.blit(aviso, (tela_x // 2 - aviso.get_width() // 2, box_y + box_height - 60))

        pygame.display.update()
        texto = reconhecer_lets_race()
        if texto.strip().lower() == "let's race":
            break

# --- INÍCIO DO JOGO ---
jogador_nome = pedir_nome()
menu(jogador_nome)