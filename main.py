import pygame, pyttsx3, random, math, speech_recognition as sr

from resources.recs import inicializarBancoDeDados, escreverDados, limpa_tela, aguarde

# variaveis

pygame.init()
inicializarBancoDeDados()
tela_x = 1000
tela_y = 700
tamanho = (tela_x, tela_y)
relogio = pygame.time.Clock()
tela = pygame.display.set_mode(tamanho)
icone = pygame.image.load('resources/imgs/icone.png')
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
fundo_menu = pygame.image.load('resources/imgs/fundo_menu.png')
fundo_game = pygame.image.load('resources/imgs/fundo_game.png')
runner = pygame.image.load('resources/imgs/runner.png')
enemy = pygame.image.load('resources/imgs/enemy.png')

# Sons

musica_menu = pygame.mixer.Sound('resources/sounds/menu.wav')
musica_game = pygame.mixer.Sound('resources/sounds/game.wav')
botoes = pygame.mixer.Sound('resources/sounds/botoes.wav')
enemySound = pygame.mixer.Sound('resources/sounds/enemy.wav')
engineSound = pygame.mixer.Sound('resources/sounds/engine.wav')
botoes.set_volume(0.5)
musica_game.set_volume(0.5)
musica_menu.set_volume(0.5)



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
    lanes = [75, 220, 370, 520, 665, 827]  # Corrigi um valor duplicado

    tamanho_runner = (100, 100)
    tamanho_enemy = (100, 100)

    posicao_runner = [tamanho[0] // 2, tamanho[1] - tamanho_runner[1]]

    inimigos = []  # Lista para armazenar inimigos

    velocidade_enemy = 5
    pontuacao = 0

    # Tempo aleatório inicial para spawnar inimigo (2 a 3 segundos)
    enemy_spawn_time = random.randint(2000, 3000)
    ultimo_spawn = pygame.time.get_ticks()

    pontos = 0
    velocidade = 5
    difficulty = 30
    paused = False
    frame = 0

    pygame.mixer.Sound.play(enemySound)

    pause_blink = True
    pause_blink_timer = 0
    pause_blink_interval = 2000  # 2 segundos em milissegundos

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if not paused:
                    if evento.key == pygame.K_LEFT and posicao_runner[0] > 0:
                        posicao_runner[0] -= 10
                    elif evento.key == pygame.K_RIGHT and posicao_runner[0] < tela_x - tamanho_runner[0]:
                        posicao_runner[0] += 10
                if evento.key == pygame.K_BACKSPACE:
                    botoes.play()
                    menu()
                elif evento.key == pygame.K_ESCAPE:
                    paused = not paused
                    pause_blink = True
                    pause_blink_timer = pygame.time.get_ticks()

        if paused:
            tela.blit(fundo_game, (0, 0))
            # Controle do piscar do texto "PAUSE"
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

        # --- Spawn de inimigos ---
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_spawn >= enemy_spawn_time:
            lane_x = random.choice(lanes)
            inimigos.append([lane_x, 0])  # Adiciona inimigo na lane escolhida
            ultimo_spawn = tempo_atual
            enemy_spawn_time = random.randint(2000, 3000)  # Novo tempo aleatório para próximo spawn

        # --- Atualiza posição dos inimigos ---
        for inimigo in inimigos:
            inimigo[1] += velocidade_enemy

        # Remove inimigos que saíram da tela
        inimigos = [i for i in inimigos if i[1] < tela_y]

        # --- Desenho do jogo ---
        tela.blit(fundo_game, (0, 0))
        tela.blit(runner, posicao_runner)
        for inimigo in inimigos:
            tela.blit(enemy, inimigo)
        # ...desenhe outros elementos do jogo aqui...

        pygame.display.update()
        relogio.tick(60)

def menu():
    pygame.mixer.music.load('resources/sounds/menu.wav')
    pygame.mixer.music.play(-1)
    while True:
        tela.blit(fundo_menu, (0, 0))
        limpa_tela(tela)
        aguarde(tela, "Pressione ENTER para jogar")
        aguarde(tela, "Pressione ESC para sair")
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    botoes.play()
                    jogar()
                elif event.key == pygame.K_ESCAPE:
                    botoes.play()
                    pygame.quit()
                    exit()


        
        




jogar()



