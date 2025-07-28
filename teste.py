from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.collision import *
from PPlay.animation import *
from PPlay.keyboard import Keyboard
from PPlay.mouse import *
from PPlay.sound import * # Importar a classe Sound
import random

# --- Constantes Globais ---
# Configurações da Janela
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
GAME_TITLE = "Corona Invaders"
BACKGROUND_COLOR = (0, 0, 0) # Cor preta para o fundo

# Power-Ups
POWERUP_SHIELD_PATH = "assets/powerup_shield.png"
POWERUP_FAST_SHOT_PATH = "assets/powerup_fast_shot.png"
POWERUP_DROP_CHANCE = 0.10 # Chance de um power-up cair (10%)
POWERUP_SPEED = 100 # Velocidade de queda dos power-ups
POWERUP_SHIELD_DURATION = 5.0 # Duração do escudo em segundos
POWERUP_FAST_SHOT_DURATION = 5.0 # Duração do tiro rápido em segundos
FAST_SHOT_COOLDOWN_MULTIPLIER = 0.5 # Multiplicador para o cooldown de tiro (ex: 0.5 = metade do tempo)
POWERUP_TYPE_SHIELD = 0
POWERUP_TYPE_FAST_SHOT = 1

# Estados do Jogo
GAME_STATE_MENU = 1
GAME_STATE_PLAYING = 2
GAME_STATE_DIFFICULTY = 3
GAME_STATE_RANKING = 4
GAME_STATE_EXIT = 5

# Dificuldades
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

# Configurações do Jogo
INITIAL_DIFFICULTY = DIFFICULTY_MEDIUM # Dificuldade inicial padrão
PLAYER_INITIAL_LIVES_BASE = 6
PLAYER_INITIAL_POS_OFFSET_Y = 5
PLAYER_SPEED_MULTIPLIER = 10
PLAYER_SHOOT_COOLDOWN = 0.5
BULLET_SPEED_MULTIPLIER = -7 # Negativo para ir para cima
ENEMY_INITIAL_ROWS_BASE = 0
ENEMY_INITIAL_COLUMNS_BASE = 1
ENEMY_INITIAL_Y_OFFSET = 50
ENEMY_MOVEMENT_BASE_SPEED = 2
ENEMY_ADVANCE_COOLDOWN = 0.15
ENEMY_ADVANCE_Y_OFFSET = 20
ENEMY_SHOT_COOLDOWN_BASE = 4
ENEMY_BULLET_SPEED_BASE = 2
ENEMY_BULLET_SPEED_FACTOR_QUANTITY = 0.2
ENEMY_BULLET_SPEED_FACTOR_LEVEL = 0.5
ENEMY_BULLET_SPEED_QUANTITY_DIVISOR = 70 # Valor original na fórmula da velocidade do tiro inimigo
ENEMY_HORIZONTAL_SPACING = 15  # Espaçamento horizontal entre inimigos
ENEMY_VERTICAL_SPACING = 15    # Espaçamento vertical entre inimigos
SCORE_HIT_ENEMY_BASE = 50
SCORE_PASS_LEVEL_BASE = 1000

# Textos do Jogo
FONT_NAME = "Arial"
FONT_COLOR = (255, 255, 255)
FONT_SIZE_SMALL = 25
FONT_SIZE_MEDIUM = 28
FONT_SIZE_LARGE = 32

# PPlay FPS (usado em alguns cálculos de movimento)
PPLAY_FPS = 60 

# --- Constantes de Áudio ---
MUSIC_MENU_PATH = "assets/menu_music.ogg"
SOUND_PLAYER_SHOOT_PATH = "assets/player_shoot.ogg"
SOUND_ENEMY_EXPLOSION_PATH = "assets/enemy_explosion.ogg"
SOUND_PLAYER_HIT_PATH = "assets/player_hit.ogg"

MUSIC_VOLUME = 1 # Ajuste de 0.0 a 1.0
SOUND_VOLUME = 1 # Ajuste de 0.0 a 1.0

# --- Variáveis Globais (mantidas para o estado atual do jogo) ---
GAME_STATE = GAME_STATE_MENU
DIFICULDADE = INITIAL_DIFFICULTY 


class Jogador(object):
    def __init__(self, janela):
        self.janela = janela
        self.player = Sprite("assets/nave.png")
        self.listaTiros = []
        self.teclado = self.janela.get_keyboard()
        self.cronometroTiros = 0
        self.vidas = PLAYER_INITIAL_LIVES_BASE - DIFICULDADE
        self.set_pos()
        
        self.shoot_sound = Sound(SOUND_PLAYER_SHOOT_PATH)
        self.shoot_sound.set_volume(SOUND_VOLUME)

        # NOVO: Atributos para power-ups
        self.has_shield = False
        self.shield_timer = 0.0
        self.is_fast_shooting = False
        self.fast_shot_timer = 0.0

        # Sprite do escudo (se for uma imagem separada ou um overlay)
        # Se o escudo for um overlay/imagem separada:
        self.shield_sprite = Sprite("assets/player_shield.png") # Crie esta imagem!
        # Ajuste a escala/posição conforme necessário.
        # self.shield_sprite.set_scale(1.1) # Exemplo para deixar o escudo um pouco maior que a nave


    def set_pos(self):
        self.player.set_position(
            (self.janela.width / 2) - (self.player.width / 2),
            self.janela.height - (self.player.height + PLAYER_INITIAL_POS_OFFSET_Y)
        )

    def _draw(self):
        self.player.draw()
        for tiro in self.listaTiros:
            tiro.draw()

    def atirar(self):
        tiro = Sprite("assets/gota.png")
        tiro.set_position(
            self.player.x + self.player.width / 2 - tiro.width / 2,
            self.player.y
        )
        self.listaTiros.append(tiro)
        self.shoot_sound.play()

    def atualizarTiros(self):
        tiros_a_manter = []
        for tiro in self.listaTiros:
            tiro.move_y(self.janela.delta_time() * PPLAY_FPS * BULLET_SPEED_MULTIPLIER)
            if tiro.y > 0:
                tiros_a_manter.append(tiro)
        self.listaTiros = tiros_a_manter

    def run(self):        
        self.player.move_key_x(PLAYER_SPEED_MULTIPLIER * self.janela.delta_time() * PPLAY_FPS)
        
        self.cronometroTiros += self.janela.delta_time()

        # NOVO: Ajustar cooldown de tiro se fast shot estiver ativo
        current_shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        if self.is_fast_shooting:
            current_shoot_cooldown *= FAST_SHOT_COOLDOWN_MULTIPLIER

        if self.cronometroTiros >= current_shoot_cooldown: # Usar o cooldown ajustado
            if self.teclado.key_pressed("SPACE"):
                self.atirar()
                self.cronometroTiros = 0

        if self.player.x < 0:
            self.player.set_position(0, self.player.y)
        elif self.player.x + self.player.width > self.janela.width:
            self.player.x = self.janela.width - self.player.width
        
        self.atualizarTiros()
        self._draw()

        if self.has_shield:
            self.shield_timer -= self.janela.delta_time()
            # Posiciona o escudo na mesma posição do jogador
            self.shield_sprite.set_position(
                self.player.x + (self.player.width - self.shield_sprite.width) / 2, # Centraliza
                self.player.y + (self.player.height - self.shield_sprite.height) / 2 # Centraliza
            )
            self.shield_sprite.draw()
            if self.shield_timer <= 0:
                self.has_shield = False

        if self.is_fast_shooting:
            self.fast_shot_timer -= self.janela.delta_time()
            if self.fast_shot_timer <= 0:
                self.is_fast_shooting = False

class Inimigos(object):
    def __init__(self, janela, nivel):
        self.janela = janela
        self.nivel = nivel
        self.matrizInimigos = []
        self.quantidadeColunas = DIFICULDADE + ENEMY_INITIAL_COLUMNS_BASE
        self.quantidadeLinhas = DIFICULDADE + ENEMY_INITIAL_ROWS_BASE
        self.quantidadeInimigos = self.quantidadeColunas * self.quantidadeLinhas
        self.velocidadeInimigos = 0 
        self.direcaoInimigos = 1
        self.listaTiros = []
        self.cronometroTiro = 0
        self.cronometroAvancar = 0
        self.velocidadeTiro = 0 
        self.spawn()

    def spawn(self):
        self.matrizInimigos.clear()
        
        temp_enemy = Sprite("assets/corona.png")
        enemy_width = temp_enemy.width
        enemy_height = temp_enemy.height

        total_width_of_enemies_grid = (self.quantidadeColunas * enemy_width) + ((self.quantidadeColunas - 1) * ENEMY_HORIZONTAL_SPACING)
        start_x = (self.janela.width - total_width_of_enemies_grid) / 2

        start_y = ENEMY_INITIAL_Y_OFFSET

        for i in range(self.quantidadeLinhas):
            self.matrizInimigos.append([])
            for j in range(self.quantidadeColunas):
                inimigo = Sprite("assets/corona.png")
                
                pos_x = start_x + j * (enemy_width + ENEMY_HORIZONTAL_SPACING)
                pos_y = start_y + i * (enemy_height + ENEMY_VERTICAL_SPACING)

                inimigo.set_position(pos_x, pos_y)
                self.matrizInimigos[i].append(inimigo)
        self.quantidadeInimigos = sum(len(linha) for linha in self.matrizInimigos)

    def moverInimigos(self):
        if self.quantidadeInimigos > 0:
            self.velocidadeInimigos = (
                self.janela.delta_time() * PPLAY_FPS * self.direcaoInimigos *
                (ENEMY_MOVEMENT_BASE_SPEED + DIFICULDADE / 3 + 2 / self.quantidadeInimigos)
            )
        
        for linha in self.matrizInimigos:
            for inimigo in linha:
                inimigo.move_x(self.velocidadeInimigos)
    
    def atirar(self):
        cooldown_necessario = ENEMY_SHOT_COOLDOWN_BASE / DIFICULDADE + (self.nivel * 0.5)
        self.cronometroTiro += self.janela.delta_time()

        if self.cronometroTiro > cooldown_necessario and self.quantidadeInimigos > 0:
            inimigos_achatados = [inimigo for linha in self.matrizInimigos for inimigo in linha]
            if inimigos_achatados:
                inimigo_atirador = random.choice(inimigos_achatados)
                tiro = Sprite("assets/tirocorona.png")
                tiro.set_position(
                    inimigo_atirador.x + inimigo_atirador.width / 2 - tiro.width / 2,
                    inimigo_atirador.y
                )
                self.listaTiros.append(tiro)
                self.cronometroTiro = 0

    def atualizarTiros(self):
        if self.quantidadeInimigos > 0:
            self.velocidadeTiro = (
                ENEMY_BULLET_SPEED_BASE + 
                (ENEMY_BULLET_SPEED_QUANTITY_DIVISOR / self.quantidadeInimigos) * ENEMY_BULLET_SPEED_FACTOR_QUANTITY + 
                self.nivel * ENEMY_BULLET_SPEED_FACTOR_LEVEL
            )
        else:
            self.velocidadeTiro = ENEMY_BULLET_SPEED_BASE

        tiros_a_manter = []
        for tiro in self.listaTiros:
            tiro.move_y(self.janela.delta_time() * PPLAY_FPS * self.velocidadeTiro)
            if tiro.y < self.janela.height:
                tiros_a_manter.append(tiro)
        self.listaTiros = tiros_a_manter

    def checarLimitesLaterais(self):
        for linha in self.matrizInimigos:
            for inimigo in linha:
                if inimigo.x <= 0 or inimigo.x >= (self.janela.width - inimigo.width):
                    return True
        return False

    def avancarInimigos(self):
        self.cronometroAvancar += self.janela.delta_time()
        if self.cronometroAvancar > ENEMY_ADVANCE_COOLDOWN:
            if self.checarLimitesLaterais():
                self.direcaoInimigos *= -1
                for linha in self.matrizInimigos:
                    for inimigo in linha:
                        inimigo.y += ENEMY_ADVANCE_Y_OFFSET
                self.cronometroAvancar = 0

    def _draw(self):
        for linha in self.matrizInimigos:
            for inimigo in linha:
                inimigo.draw()
                
        for tiro in self.listaTiros:
            tiro.draw()
    
    def run(self):
        self.moverInimigos()
        self.avancarInimigos()
        self.atirar()
        self.atualizarTiros()
        self._draw()

class PowerUp(object):
    def __init__(self, janela, x, y, type_id):
        self.janela = janela
        self.type_id = type_id
        self.sprite = None

        # Carrega a imagem do power-up com base no tipo
        if self.type_id == POWERUP_TYPE_SHIELD:
            self.sprite = Sprite(POWERUP_SHIELD_PATH)
        elif self.type_id == POWERUP_TYPE_FAST_SHOT:
            self.sprite = Sprite(POWERUP_FAST_SHOT_PATH)
        # elif self.type_id == POWERUP_TYPE_LIFE: # Para futura implementação
        #     self.sprite = Sprite(POWERUP_LIFE_PATH)
        # elif self.type_id == POWERUP_TYPE_TRIPLE_SHOT: # Para futura implementação
        #     self.sprite = Sprite(POWERUP_TRIPLE_SHOT_PATH)

        if self.sprite: # Garante que um sprite foi carregado
            self.sprite.set_position(x, y)
        else:
            print(f"Erro: Sprite para PowerUp tipo {type_id} não encontrado.")


    def run(self):
        if self.sprite:
            # Move o power-up para baixo
            self.sprite.move_y(self.janela.delta_time() * POWERUP_SPEED)
            self.sprite.draw()

    # Métodos auxiliares para colisão
    def get_x(self):
        return self.sprite.x
    
    def get_y(self):
        return self.sprite.y
    
    def get_width(self):
        return self.sprite.width

    def get_height(self):
        return self.sprite.height

    def collided(self, other_sprite):
        if self.sprite:
            return Collision.collided(self.sprite, other_sprite)
        return False

class Jogar(object):
    def __init__(self, janela):
        self.janela = janela
        self.pontuacao = 0
        self.tempo = 0
        self.nivel = 1
        self.fps_counter = 0
        self.current_fps = 0
        self.fps_timer = 0
        self.teclado = janela.get_keyboard()
        self.jogador = Jogador(self.janela)
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.vivo = True
        self.active_powerups = []

        # Animação de morte/respawn do jogador (já existe)
        self.playerDead = Animation("assets/jogo_jogador-respawn.png", 12)
        self.playerDead.set_total_duration(1000) # 1 segundo
        self.death_animation_timer = 1 # Usado para controlar quando a animação termina para o jogador

        # NOVO: Animação de explosão para inimigos
        # Usaremos a mesma animação do player para economizar recursos e manter consistência
        self.enemy_explosion_animation_template = Animation("assets/jogo_jogador-respawn.png", 12)
        self.enemy_explosion_animation_template.set_total_duration(500) # Mais rápida para inimigos (0.5 segundos)
        
        # Lista para gerenciar as animações de explosão ativas dos inimigos
        self.active_enemy_explosions = [] 
        
        # Carregar os sons do jogo
        self.enemy_explosion_sound = Sound(SOUND_ENEMY_EXPLOSION_PATH)
        self.enemy_explosion_sound.set_volume(SOUND_VOLUME)
        self.player_hit_sound = Sound(SOUND_PLAYER_HIT_PATH)
        self.player_hit_sound.set_volume(SOUND_VOLUME)

    def TiroNoInimigo(self):
        for i, linha in enumerate(self.inimigos.matrizInimigos):
            for j, inimigo in enumerate(linha):
                for k, tiro_jogador in enumerate(self.jogador.listaTiros):
                    if Collision.collided(tiro_jogador, inimigo):
                        self.pontuacao += SCORE_HIT_ENEMY_BASE + SCORE_HIT_ENEMY_BASE / max(1, self.tempo)
                        
                        # INÍCIO NOVO: Lógica de drop de power-up
                        if random.random() < POWERUP_DROP_CHANCE: # Chance de dropar
                            # Escolhe um tipo de power-up aleatoriamente entre os disponíveis
                            powerup_type = random.choice([POWERUP_TYPE_SHIELD, POWERUP_TYPE_FAST_SHOT])
                            new_powerup = PowerUp(self.janela, inimigo.x, inimigo.y, powerup_type)
                            self.active_powerups.append(new_powerup)
                        # FIM NOVO: Lógica de drop de power-up

                        new_explosion = Animation("assets/jogo_jogador-respawn.png", 12)
                        new_explosion.set_total_duration(self.enemy_explosion_animation_template.total_duration)
                        new_explosion.set_position(inimigo.x, inimigo.y)
                        new_explosion.animation_timer = 0.0
                        self.active_enemy_explosions.append(new_explosion)

                        self.inimigos.matrizInimigos[i].pop(j)
                        self.jogador.listaTiros.pop(k)
                        self.enemy_explosion_sound.play() 
                        if not self.inimigos.matrizInimigos[i]:
                            self.inimigos.matrizInimigos.pop(i)
                        self.inimigos.quantidadeInimigos = sum(len(linha) for linha in self.inimigos.matrizInimigos)
                        return

    def reset(self):
        self.nivel = 1
        self.pontuacao = 0
        self.vivo = True
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.jogador = Jogador(self.janela)
        self.death_animation_timer = 1

    def PassarDeNivel(self):
        self.pontuacao += self.nivel * SCORE_PASS_LEVEL_BASE
        self.nivel += 1
        self.inimigos.quantidadeColunas += 1 
        self.inimigos.quantidadeLinhas += 1
        self.inimigos.direcaoInimigos *= 1.2
        self.jogador.listaTiros.clear()
        self.inimigos.listaTiros.clear()
        self.tempo = 0
        self.inimigos.spawn()
        self.inimigos.quantidadeInimigos = sum(len(linha) for linha in self.inimigos.matrizInimigos)

    def checarGameOverY(self):
        for linha in self.inimigos.matrizInimigos:
            for inimigo in linha:
                if inimigo.y + inimigo.height >= self.jogador.player.y:
                    return True
        return False

    def TiroNoPlayer(self):
        for i, tiro_inimigo in enumerate(self.inimigos.listaTiros):
            if Collision.collided(tiro_inimigo, self.jogador.player):
                # NOVO: Verificar se o jogador tem escudo
                if self.jogador.has_shield:
                    self.jogador.has_shield = False # Escudo é quebrado
                    self.inimigos.listaTiros.pop(i) # Remove o tiro inimigo
                    # Opcional: Adicionar um som ou efeito visual para quebrar o escudo
                    return # Não perde vida, sai da função
                
                # Se não tem escudo, a lógica de perda de vida continua
                self.jogador.vidas -= 1
                self.inimigos.listaTiros.pop(i)
                self.player_hit_sound.play()
                self.death_animation_timer = 0
                self.playerDead.set_curr_frame(0)
                self.playerDead.set_position(
                    (self.janela.width / 2) - (self.jogador.player.width / 2),
                    self.janela.height - (self.jogador.player.height + PLAYER_INITIAL_POS_OFFSET_Y)
                )
                if self.jogador.vidas != 0:
                    self.respawn()
                break

    def respawn(self):            
        self.jogador.player.set_position(
            (self.janela.width / 2) - (self.jogador.player.width / 2),
            self.janela.height - (self.jogador.player.height + PLAYER_INITIAL_POS_OFFSET_Y)
        )

    def gameOver(self):            
        try:
            with open('ranking.txt','r') as arq:
                conteudo = arq.readlines()
        except FileNotFoundError:
            conteudo = []

        nome=str(input('Digite seu nome: '))
        
        if DIFICULDADE == DIFFICULTY_EASY:
            self.nivelfinal = "fácil"
        elif DIFICULDADE == DIFFICULTY_MEDIUM:
            self.nivelfinal = "médio"
        elif DIFICULDADE == DIFFICULTY_HARD:
            self.nivelfinal = "difícil"
        
        linha = f"{nome} {self.nivelfinal} {int(self.pontuacao)}\n"
        conteudo.append(linha)
        
        with open('ranking.txt', 'w') as arq:
            arq.writelines(conteudo)
        
        print('Ranking atualizado com sucesso')
        
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.jogador = Jogador(self.janela)
        self.reset()
        global GAME_STATE
        GAME_STATE = GAME_STATE_MENU

    def run(self):
        self.fps_timer += self.janela.delta_time()
        self.fps_counter += 1
        if self.fps_timer > 1: 
            self.current_fps = self.fps_counter   
            self.fps_counter = 0
            self.fps_timer = 0
            
        if self.vivo: 
            if self.inimigos.quantidadeInimigos == 0:
                self.PassarDeNivel()
            self.inimigos.run()
            self.jogador.run()
            self.TiroNoInimigo()
            self.TiroNoPlayer()

            self.tempo += self.janela.delta_time()
            
            if self.teclado.key_pressed("ESC"):
                global GAME_STATE
                GAME_STATE = GAME_STATE_MENU
                self.reset()

            if self.checarGameOverY() or self.jogador.vidas == 0:
                self.nivel = 1
                self.vivo = False

            self.janela.draw_text(
                f"Vidas: {self.jogador.vidas}", 300, 5, 
                size=FONT_SIZE_MEDIUM, color=FONT_COLOR, font_name=FONT_NAME
            )
            self.janela.draw_text(
                f"FPS:{self.current_fps}", 0, 0, 
                size=FONT_SIZE_SMALL, color=FONT_COLOR, font_name=FONT_NAME
            )
            self.janela.draw_text(
                f"Nivel: {self.nivel}", 400, 5, 
                size=FONT_SIZE_MEDIUM, color=FONT_COLOR, font_name=FONT_NAME
            )
            self.janela.draw_text(
                f"Pontos: {int(self.pontuacao)}", 500, 5, 
                size=FONT_SIZE_MEDIUM, color=FONT_COLOR, font_name=FONT_NAME
            )

            # NOVO: Desenhar e atualizar animações de explosão dos inimigos
            explosions_to_keep = []
            for explosion in self.active_enemy_explosions:
                explosion.draw()
                explosion.update()
                
                # Incrementa o timer da explosão
                explosion.animation_timer += self.janela.delta_time()
                
                # Se o timer da explosão for maior ou igual à duração total da animação, ela terminou.
                # Lembre-se que total_duration é em milissegundos, e delta_time é em segundos.
                if explosion.animation_timer >= (explosion.total_duration / 1000.0):
                    # A animação terminou, não a adiciona de volta à lista de "a manter"
                    pass 
                else:
                    explosions_to_keep.append(explosion)
            self.active_enemy_explosions = explosions_to_keep # Atualiza a lista com as explosões que ainda estão ativas

        # Gerenciar Power-ups
            powerups_to_keep = []
            for powerup in self.active_powerups:
                powerup.run() # Atualiza posição e desenha o power-up
                
                # Checar colisão com o jogador
                if powerup.collided(self.jogador.player):
                    # Aplica o efeito do power-up
                    if powerup.type_id == POWERUP_TYPE_SHIELD:
                        self.jogador.has_shield = True
                        self.jogador.shield_timer = POWERUP_SHIELD_DURATION
                    elif powerup.type_id == POWERUP_TYPE_FAST_SHOT:
                        self.jogador.is_fast_shooting = True
                        self.jogador.fast_shot_timer = POWERUP_FAST_SHOT_DURATION
                    # Não adiciona o power-up à lista de "a manter" (ele foi coletado)
                elif powerup.get_y() < self.janela.height: # Se o power-up ainda está na tela (não caiu)
                    powerups_to_keep.append(powerup)
            self.active_powerups = powerups_to_keep # Atualiza a lista

        else: # Se o jogador não estiver mais vivo (Game Over)
            self.gameOver()

        # Animação de morte do jogador (já existe)
        if self.death_animation_timer < 0.9:
            self.playerDead.draw()
            self.playerDead.update()
            self.death_animation_timer += self.janela.delta_time()

class DificuldadeConstantes:
    EASY_BUTTON_COORDS = (241, 180, 470, 230)
    MEDIUM_BUTTON_COORDS = (241, 265, 470, 315)
    HARD_BUTTON_COORDS = (335, 350, 470, 410) 
    BACK_BUTTON_COORDS = (335, 470, 565, 527)

class Dificuldade(object):
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.teclado = self.janela.get_keyboard() 

        self.tela = GameImage("assets/dificuldade.png")

    def _check_button_click(self, coords, difficulty_value=None, game_state_change=None):
        if self.mouse.is_over_area(start_point=(coords[0], coords[1]), end_point=(coords[2], coords[3])):
            if self.mouse.is_button_pressed(1):
                global DIFICULDADE, GAME_STATE
                if difficulty_value is not None:
                    DIFICULDADE = difficulty_value
                if game_state_change is not None:
                    GAME_STATE = game_state_change
                return True 
        return False

    def run(self):
        self.tela.draw()

        self._check_button_click(DificuldadeConstantes.EASY_BUTTON_COORDS, difficulty_value=DIFFICULTY_EASY)
        self._check_button_click(DificuldadeConstantes.MEDIUM_BUTTON_COORDS, difficulty_value=DIFFICULTY_MEDIUM)
        self._check_button_click(DificuldadeConstantes.HARD_BUTTON_COORDS, difficulty_value=DIFFICULTY_HARD)

        global GAME_STATE
        self._check_button_click(DificuldadeConstantes.BACK_BUTTON_COORDS, game_state_change=GAME_STATE_MENU) 
        
        if self.teclado.key_pressed("ESC"):
            GAME_STATE = GAME_STATE_MENU 

class Menu(object):
    def __init__(self, janela):
        self.janela = janela
        self.tela = GameImage("assets/menu.png")
        self.teclado = Window.get_keyboard()
        self.mouse = Window.get_mouse()

    def run(self):
        self.tela.draw()
        global GAME_STATE

        if self.mouse.is_over_area(start_point=(335,180),end_point=(567,230)):
            if self.mouse.is_button_pressed(1):
                GAME_STATE = GAME_STATE_PLAYING

        if self.mouse.is_over_area(start_point=(335,265),end_point=(567,315)):
            if self.mouse.is_button_pressed(1):
                GAME_STATE = GAME_STATE_DIFFICULTY

        if self.mouse.is_over_area(start_point=(335,350),end_point=(567,400)):
            if self.mouse.is_button_pressed(1):
                GAME_STATE = GAME_STATE_RANKING

        if self.mouse.is_over_area(start_point=(335,435),end_point=(567,485)):
            if self.mouse.is_button_pressed(1):
                GAME_STATE = GAME_STATE_EXIT

class Ranking(object):
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.titulo = Sprite("assets/ranking_titulo.png", 1)
        self.set_pos()

    def set_pos(self):
        self.titulo.set_position(self.janela.width/2 - self.titulo.width/2, 25)

    def _draw(self):
        self.titulo.draw()

    def run(self):
        self._draw()
        try:
            with open('ranking.txt','r') as arq:
                conteudo = arq.readlines()
        except FileNotFoundError:
            conteudo = []

        nomes = []
        dificuldades = []
        pontos = []

        for linha_str in conteudo:
            linha_split = linha_str.split()
            if len(linha_split) >= 3:
                nomes.append(linha_split[0])
                dificuldades.append(linha_split[1])
                try:
                    pontos.append(int(linha_split[2]))
                except ValueError:
                    pontos.append(0)
            else:
                pass

        for _ in range(len(pontos)):
            for i in range(len(pontos) - 1):
                if pontos[i] < pontos[i+1]:
                    pontos[i+1], pontos[i] = pontos[i], pontos[i+1]
                    nomes[i+1], nomes[i] = nomes[i], nomes[i+1]
                    dificuldades[i+1], dificuldades[i] = dificuldades[i], dificuldades[i+1]

        for i in range(min(5, len(nomes))):
            self.janela.draw_text(
                f"{i+1}º {nomes[i]} - Pontos: {pontos[i]} - Dificuldade: {dificuldades[i]}", 
                200, 100 + i * 50, 
                size=FONT_SIZE_LARGE, color=FONT_COLOR, font_name=FONT_NAME
            )
        
        global GAME_STATE
        if self.teclado.key_pressed("ESC"):
            GAME_STATE = GAME_STATE_MENU

# --- Inicialização do Jogo ---
janela = Window(WINDOW_WIDTH, WINDOW_HEIGHT)
janela.set_title(GAME_TITLE)
teclado = Window.get_keyboard()
mouse = Window.get_mouse()

menu = Menu(janela)
dificuldade = Dificuldade(janela)
ranking = Ranking(janela)
jogo = Jogar(janela)

# Carregar e configurar a música do menu aqui
menu_music = Sound(MUSIC_MENU_PATH)
menu_music.set_volume(MUSIC_VOLUME)

# No loop principal do jogo

# --- Loop Principal do Jogo ---
while GAME_STATE != GAME_STATE_EXIT:
    janela.set_background_color(BACKGROUND_COLOR)

    # Lógica para tocar/parar a música de fundo
    # REMOVA A LÓGICA ANTERIOR E COLOQUE ESTA ABAIXO:
    if not menu_music.is_playing(): # A música sempre deve tocar, a menos que não esteja já tocando
        menu_music.play()

    if GAME_STATE == GAME_STATE_MENU:
        menu.run()

    elif GAME_STATE == GAME_STATE_PLAYING:
        jogo.run()

    elif GAME_STATE == GAME_STATE_DIFFICULTY:
        dificuldade.run()
        jogo = Jogar(janela) 
        
    elif GAME_STATE == GAME_STATE_RANKING:
        ranking.run()

    janela.update()