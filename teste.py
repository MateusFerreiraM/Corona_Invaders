#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.collision import *
from PPlay.animation import *
from PPlay.keyboard import Keyboard
from PPlay.mouse import *
from PPlay.sound import *
import random
import string

# --- Constantes de Configuração ---

# Janela e Título
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
GAME_TITLE = "Corona Invaders"
BACKGROUND_COLOR = (0, 0, 0)

# Estados do Jogo
GAME_STATE_MENU = 1
GAME_STATE_PLAYING = 2
GAME_STATE_DIFFICULTY = 3
GAME_STATE_RANKING = 4
GAME_STATE_GAME_OVER = 5
GAME_STATE_EXIT = 6

# Dificuldades
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

# Caminhos dos Assets (Paths)
ASSET_PATH = "assets/"
FONT_NAME = "Arial"

# Áudio
# ALTERAÇÃO: Apenas uma música de fundo
MUSIC_BACKGROUND_PATH = ASSET_PATH + "game_music.ogg" 
SOUND_PLAYER_SHOOT_PATH = ASSET_PATH + "player_shoot.ogg"
SOUND_ENEMY_EXPLOSION_PATH = ASSET_PATH + "enemy_explosion.ogg"
SOUND_PLAYER_HIT_PATH = ASSET_PATH + "player_hit.ogg"

# Imagens
PLAYER_SPRITE_PATH = ASSET_PATH + "nave.png"
PLAYER_SHIELD_SPRITE_PATH = ASSET_PATH + "player_shield.png"
PLAYER_DEATH_ANIM_PATH = ASSET_PATH + "jogo_jogador-respawn.png"
ENEMY_SPRITE_PATH = ASSET_PATH + "corona.png"
PLAYER_BULLET_PATH = ASSET_PATH + "gota.png"
ENEMY_BULLET_PATH = ASSET_PATH + "tirocorona.png"
POWERUP_SHIELD_PATH = ASSET_PATH + "powerup_shield.png"
POWERUP_FAST_SHOT_PATH = ASSET_PATH + "powerup_fast_shot.png"
MENU_BACKGROUND_PATH = ASSET_PATH + "menu.png"
DIFFICULTY_BACKGROUND_PATH = ASSET_PATH + "dificuldade.png"
RANKING_TITLE_PATH = ASSET_PATH + "ranking_titulo.png"

# --- Constantes de Gameplay ---

# Jogador
PLAYER_INITIAL_LIVES_BASE = 6
PLAYER_SPEED = 600
PLAYER_SHOOT_COOLDOWN = 0.5
PLAYER_INITIAL_POS_OFFSET_Y = 5

# Inimigos
ENEMY_INITIAL_ROWS_BASE = 0
ENEMY_INITIAL_COLUMNS_BASE = 1
ENEMY_INITIAL_Y_OFFSET = 50
ENEMY_MOVEMENT_BASE_SPEED = 120
ENEMY_ADVANCE_COOLDOWN = 0.15
ENEMY_ADVANCE_Y_OFFSET = 20
ENEMY_SHOT_COOLDOWN_BASE = 4
ENEMY_HORIZONTAL_SPACING = 15
ENEMY_VERTICAL_SPACING = 15

# Projéteis
BULLET_SPEED_PLAYER = -420
ENEMY_BULLET_SPEED_BASE = 120
ENEMY_BULLET_SPEED_FACTOR_QUANTITY = 0.2
ENEMY_BULLET_SPEED_FACTOR_LEVEL = 0.5
ENEMY_BULLET_SPEED_QUANTITY_DIVISOR = 70

# Power-Ups
POWERUP_DROP_CHANCE = 0.10
POWERUP_SPEED = 100
POWERUP_SHIELD_DURATION = 5.0
POWERUP_FAST_SHOT_DURATION = 5.0
FAST_SHOT_COOLDOWN_MULTIPLIER = 0.5
POWERUP_TYPE_SHIELD = 0
POWERUP_TYPE_FAST_SHOT = 1

# Pontuação
SCORE_HIT_ENEMY_BASE = 50
SCORE_PASS_LEVEL_BASE = 1000

# UI e Texto
FONT_COLOR = (255, 255, 255)
FONT_SIZE_SMALL = 25
FONT_SIZE_MEDIUM = 28
FONT_SIZE_LARGE = 32

# Arquivos
RANKING_FILE = 'ranking.txt'

# --- Variáveis Globais de Estado ---
GAME_CURRENT_STATE = GAME_STATE_MENU
DIFFICULTY_LEVEL = DIFFICULTY_MEDIUM

# --- Classes do Jogo ---

class AssetManager:
    """Classe para pré-carregar sons e evitar carregamento durante o jogo."""
    def __init__(self):
        self.player_shoot = Sound(SOUND_PLAYER_SHOOT_PATH)
        self.player_hit = Sound(SOUND_PLAYER_HIT_PATH)
        self.enemy_explosion = Sound(SOUND_ENEMY_EXPLOSION_PATH)
        # ALTERAÇÃO: Carrega apenas uma música
        self.background_music = Sound(MUSIC_BACKGROUND_PATH)
        
    def set_volume(self, volume):
        vol_int = int(volume * 100)
        self.player_shoot.set_volume(vol_int)
        self.player_hit.set_volume(vol_int)
        self.enemy_explosion.set_volume(vol_int)
        self.background_music.set_volume(vol_int)

class Jogador:
    """Gerencia o jogador, seus movimentos, tiros e power-ups."""
    def __init__(self, janela, assets):
        self.janela = janela
        self.assets = assets
        self.player = Sprite(PLAYER_SPRITE_PATH)
        self.shield_sprite = Sprite(PLAYER_SHIELD_SPRITE_PATH)
        self.listaTiros = []
        self.teclado = self.janela.get_keyboard()
        self.cronometroTiros = 0
        self.vidas = PLAYER_INITIAL_LIVES_BASE - DIFFICULTY_LEVEL
        
        self.has_shield = False
        self.shield_timer = 0.0
        self.is_fast_shooting = False
        self.fast_shot_timer = 0.0
        
        self.set_initial_pos()

    def set_initial_pos(self):
        self.player.set_position(
            (self.janela.width / 2) - (self.player.width / 2),
            self.janela.height - (self.player.height + PLAYER_INITIAL_POS_OFFSET_Y)
        )

    def atirar(self):
        tiro = Sprite(PLAYER_BULLET_PATH)
        tiro.set_position(self.player.x + self.player.width / 2 - tiro.width / 2, self.player.y)
        self.listaTiros.append(tiro)
        self.assets.player_shoot.play()

    def _handle_input(self):
        dt = self.janela.delta_time()
        if self.teclado.key_pressed("LEFT"):
            self.player.x -= PLAYER_SPEED * dt
        if self.teclado.key_pressed("RIGHT"):
            self.player.x += PLAYER_SPEED * dt

        current_shoot_cooldown = PLAYER_SHOOT_COOLDOWN * (FAST_SHOT_COOLDOWN_MULTIPLIER if self.is_fast_shooting else 1)
        if self.teclado.key_pressed("SPACE") and self.cronometroTiros >= current_shoot_cooldown:
            self.atirar()
            self.cronometroTiros = 0

    def _update_timers(self):
        dt = self.janela.delta_time()
        self.cronometroTiros += dt
        
        if self.has_shield:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.has_shield = False
        
        if self.is_fast_shooting:
            self.fast_shot_timer -= dt
            if self.fast_shot_timer <= 0:
                self.is_fast_shooting = False

    def _update_positions(self):
        self.player.x = max(0, min(self.player.x, self.janela.width - self.player.width))
        
        self.listaTiros = [tiro for tiro in self.listaTiros if tiro.y > -tiro.height]
        for tiro in self.listaTiros:
            tiro.move_y(BULLET_SPEED_PLAYER * self.janela.delta_time())

    def draw(self):
        self.player.draw()
        for tiro in self.listaTiros:
            tiro.draw()
        
        if self.has_shield:
            self.shield_sprite.set_position(
                self.player.x + (self.player.width - self.shield_sprite.width) / 2,
                self.player.y + (self.player.height - self.shield_sprite.height) / 2
            )
            self.shield_sprite.draw()

    def run(self):
        self._handle_input()
        self._update_timers()
        self._update_positions()
        self.draw()

class Inimigos:
    """Gerencia o exército de inimigos, seus movimentos e tiros."""
    def __init__(self, janela, nivel, dificuldade):
        self.janela = janela
        self.nivel = nivel
        self.dificuldade = dificuldade
        self.matrizInimigos = []
        self.quantidadeColunas = self.dificuldade + ENEMY_INITIAL_COLUMNS_BASE + (nivel -1)
        self.quantidadeLinhas = self.dificuldade + ENEMY_INITIAL_ROWS_BASE
        self.quantidadeInimigos = 0
        self.direcaoInimigos = 1
        self.listaTiros = []
        self.cronometroTiro = 0
        self.cronometroAvancar = 0
        self.spawn()

    def spawn(self):
        self.matrizInimigos.clear()
        enemy_sprite = Sprite(ENEMY_SPRITE_PATH)
        enemy_width = enemy_sprite.width
        enemy_height = enemy_sprite.height

        grid_width = (self.quantidadeColunas * enemy_width) + ((self.quantidadeColunas - 1) * ENEMY_HORIZONTAL_SPACING)
        start_x = (self.janela.width - grid_width) / 2

        for i in range(self.quantidadeLinhas):
            linha = []
            for j in range(self.quantidadeColunas):
                inimigo = Sprite(ENEMY_SPRITE_PATH)
                pos_x = start_x + j * (enemy_width + ENEMY_HORIZONTAL_SPACING)
                pos_y = ENEMY_INITIAL_Y_OFFSET + i * (enemy_height + ENEMY_VERTICAL_SPACING)
                inimigo.set_position(pos_x, pos_y)
                linha.append(inimigo)
            self.matrizInimigos.append(linha)
        
        self.quantidadeInimigos = self.quantidadeColunas * self.quantidadeLinhas

    def _move_and_advance(self):
        dt = self.janela.delta_time()
        if self.quantidadeInimigos > 0:
            speed_multiplier = (ENEMY_MOVEMENT_BASE_SPEED + self.dificuldade * 20 + 200 / self.quantidadeInimigos)
            velocidade_x = self.direcaoInimigos * speed_multiplier * dt
            for linha in self.matrizInimigos:
                for inimigo in linha:
                    inimigo.move_x(velocidade_x)

        self.cronometroAvancar += dt
        if self.cronometroAvancar > ENEMY_ADVANCE_COOLDOWN:
            atingiu_limite = any(
                inimigo.x <= 0 or (inimigo.x + inimigo.width) >= self.janela.width
                for linha in self.matrizInimigos for inimigo in linha
            )
            if atingiu_limite:
                self.direcaoInimigos *= -1
                for linha in self.matrizInimigos:
                    for inimigo in linha:
                        inimigo.y += ENEMY_ADVANCE_Y_OFFSET
                self.cronometroAvancar = 0

    def _shoot(self):
        if not self.matrizInimigos or self.quantidadeInimigos == 0:
            return

        cooldown = max(0.5, (ENEMY_SHOT_COOLDOWN_BASE / self.dificuldade) - (self.nivel * 0.2))
        self.cronometroTiro += self.janela.delta_time()

        if self.cronometroTiro > cooldown:
            self.cronometroTiro = 0
            inimigos_disponiveis = [inimigo for linha in self.matrizInimigos for inimigo in linha]
            if inimigos_disponiveis:
                atirador = random.choice(inimigos_disponiveis)
                tiro = Sprite(ENEMY_BULLET_PATH)
                tiro.set_position(atirador.x + atirador.width / 2 - tiro.width / 2, atirador.y + atirador.height)
                self.listaTiros.append(tiro)

    def _update_bullets(self):
        if self.quantidadeInimigos > 0:
            velocidade_tiro = (
                ENEMY_BULLET_SPEED_BASE + 
                (ENEMY_BULLET_SPEED_QUANTITY_DIVISOR / self.quantidadeInimigos) * ENEMY_BULLET_SPEED_FACTOR_QUANTITY + 
                self.nivel * ENEMY_BULLET_SPEED_FACTOR_LEVEL
            )
        else:
            velocidade_tiro = ENEMY_BULLET_SPEED_BASE
        
        self.listaTiros = [tiro for tiro in self.listaTiros if tiro.y < self.janela.height]
        for tiro in self.listaTiros:
            tiro.move_y(velocidade_tiro * self.janela.delta_time())

    def draw(self):
        for linha in self.matrizInimigos:
            for inimigo in linha:
                inimigo.draw()
        for tiro in self.listaTiros:
            tiro.draw()

    def run(self):
        self._move_and_advance()
        self._shoot()
        self._update_bullets()
        self.draw()

class PowerUp(Sprite):
    """Classe para os objetos de Power-up que caem na tela."""
    def __init__(self, janela, x, y, type_id):
        self.janela = janela
        self.type_id = type_id
        path = POWERUP_SHIELD_PATH if type_id == POWERUP_TYPE_SHIELD else POWERUP_FAST_SHOT_PATH
        super().__init__(path)
        self.set_position(x, y)

    def run(self):
        self.move_y(POWERUP_SPEED * self.janela.delta_time())
        self.draw()

class Jogar:
    """Classe principal que gerencia a tela de jogo."""
    def __init__(self, janela, assets, dificuldade):
        self.janela = janela
        self.assets = assets
        self.teclado = janela.get_keyboard()
        self.dificuldade = dificuldade
        self.pontuacao = 0
        self.nivel = 1
        
        self.jogador = Jogador(janela, assets)
        self.inimigos = Inimigos(janela, self.nivel, self.dificuldade)
        self.active_powerups = []
        self.active_explosions = []
        
    def _check_collisions(self):
        tiros_jogador_restantes = []
        for tiro in self.jogador.listaTiros:
            atingiu_alvo = False
            for i, linha in enumerate(self.inimigos.matrizInimigos):
                for j, inimigo in enumerate(linha):
                    if not atingiu_alvo and tiro.collided(inimigo):
                        atingiu_alvo = True
                        self.pontuacao += SCORE_HIT_ENEMY_BASE * self.dificuldade
                        self._create_explosion(inimigo.x, inimigo.y)
                        self.assets.enemy_explosion.play()

                        if random.random() < POWERUP_DROP_CHANCE:
                            p_type = random.choice([POWERUP_TYPE_SHIELD, POWERUP_TYPE_FAST_SHOT])
                            self.active_powerups.append(PowerUp(self.janela, inimigo.x, inimigo.y, p_type))

                        linha.pop(j)
                        self.inimigos.quantidadeInimigos -= 1
                        break 
                if atingiu_alvo:
                    break
            if not atingiu_alvo:
                tiros_jogador_restantes.append(tiro)
        self.jogador.listaTiros = tiros_jogador_restantes
        self.inimigos.matrizInimigos = [linha for linha in self.inimigos.matrizInimigos if linha]

        for i, tiro_inimigo in enumerate(self.inimigos.listaTiros):
            if tiro_inimigo.collided(self.jogador.player):
                self.inimigos.listaTiros.pop(i)
                self._handle_player_hit()
                break

        powerups_restantes = []
        for powerup in self.active_powerups:
            if powerup.collided(self.jogador.player):
                if powerup.type_id == POWERUP_TYPE_SHIELD:
                    self.jogador.has_shield = True
                    self.jogador.shield_timer = POWERUP_SHIELD_DURATION
                elif powerup.type_id == POWERUP_TYPE_FAST_SHOT:
                    self.jogador.is_fast_shooting = True
                    self.jogador.fast_shot_timer = POWERUP_FAST_SHOT_DURATION
            else:
                powerups_restantes.append(powerup)
        self.active_powerups = powerups_restantes
    
    def _handle_player_hit(self):
        if self.jogador.has_shield:
            self.jogador.has_shield = False
            return
            
        # ALTERAÇÃO: Cria a explosão na posição do jogador ANTES de qualquer outra ação.
        self._create_explosion(self.jogador.player.x, self.jogador.player.y)
        
        self.assets.player_hit.play()
        self.jogador.vidas -= 1
        
        if self.jogador.vidas > 0:
            # Respawn instantâneo
            self.jogador.set_initial_pos()
        else:
            # Se for a última vida, move o jogador para fora da tela para "escondê-lo"
            self.jogador.player.set_position(-1000, -1000)

    
    def _create_explosion(self, x, y):
        """Cria uma nova animação de explosão no local especificado."""
        new_explosion = Animation(PLAYER_DEATH_ANIM_PATH, 12, loop=False)
        new_explosion.set_total_duration(500)
        new_explosion.set_position(x, y)
        self.active_explosions.append(new_explosion)

    def _update_animations(self):
        self.active_explosions = [exp for exp in self.active_explosions if exp.get_curr_frame() < exp.get_final_frame() - 1]
        for exp in self.active_explosions:
            exp.update()
            
    def _draw_hud(self):
        self.janela.draw_text(f"Vidas: {self.jogador.vidas}", 10, 5, size=FONT_SIZE_MEDIUM, color=FONT_COLOR)
        self.janela.draw_text(f"Nível: {self.nivel}", self.janela.width / 2 - 50, 5, size=FONT_SIZE_MEDIUM, color=FONT_COLOR)
        self.janela.draw_text(f"Pontos: {int(self.pontuacao)}", self.janela.width - 210, 5, size=FONT_SIZE_MEDIUM, color=FONT_COLOR)

    def _check_game_over_conditions(self):
        if self.jogador.vidas <= 0:
            return True
        # Verifica se inimigos chegaram na posição Y do jogador (exceto se o jogador já morreu)
        if self.jogador.vidas > 0:
            for linha in self.inimigos.matrizInimigos:
                for inimigo in linha:
                    if (inimigo.y + inimigo.height) >= self.jogador.player.y:
                        return True
        return False

    def _level_up(self):
        self.pontuacao += self.nivel * SCORE_PASS_LEVEL_BASE
        self.nivel += 1
        self.jogador.listaTiros.clear()
        self.inimigos.listaTiros.clear()
        self.active_powerups.clear()
        self.inimigos = Inimigos(self.janela, self.nivel, self.dificuldade)

    def run(self):
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU, self.pontuacao

        self.jogador.run()
        self.inimigos.run()
        
        self.active_powerups = [p for p in self.active_powerups if p.y < self.janela.height]
        for p in self.active_powerups:
            p.run()
            
        self._check_collisions()
        self._update_animations()

        # Desenho dos elementos
        self.inimigos.draw()
        self.jogador.draw()
        
        for p in self.active_powerups:
            p.draw()
        for exp in self.active_explosions:
            exp.draw()

        self._draw_hud()

        if self._check_game_over_conditions():
            return GAME_STATE_GAME_OVER, self.pontuacao
            
        if self.inimigos.quantidadeInimigos == 0:
            self._level_up()

        return GAME_STATE_PLAYING, self.pontuacao

class Menu:
    """Tela de Menu principal."""
    def __init__(self, janela):
        self.janela = janela
        self.background = GameImage(MENU_BACKGROUND_PATH)
        self.mouse = Mouse()
        self.play_coords = (335, 180, 567, 230)
        self.diff_coords = (335, 265, 567, 315)
        self.rank_coords = (335, 350, 567, 400)
        self.exit_coords = (335, 435, 567, 485)

    def run(self):
        self.background.draw()
        
        if self.mouse.is_over_area(start_point=(self.play_coords[0], self.play_coords[1]), end_point=(self.play_coords[2], self.play_coords[3])) and self.mouse.is_button_pressed(1):
            return GAME_STATE_PLAYING
        if self.mouse.is_over_area(start_point=(self.diff_coords[0], self.diff_coords[1]), end_point=(self.diff_coords[2], self.diff_coords[3])) and self.mouse.is_button_pressed(1):
            return GAME_STATE_DIFFICULTY
        if self.mouse.is_over_area(start_point=(self.rank_coords[0], self.rank_coords[1]), end_point=(self.rank_coords[2], self.rank_coords[3])) and self.mouse.is_button_pressed(1):
            return GAME_STATE_RANKING
        if self.mouse.is_over_area(start_point=(self.exit_coords[0], self.exit_coords[1]), end_point=(self.exit_coords[2], self.exit_coords[3])) and self.mouse.is_button_pressed(1):
            return GAME_STATE_EXIT
            
        return GAME_STATE_MENU

class Dificuldade:
    """Tela para seleção de dificuldade."""
    def __init__(self, janela):
        self.janela = janela
        self.background = GameImage(DIFFICULTY_BACKGROUND_PATH)
        self.mouse = Mouse()
        self.teclado = janela.get_keyboard()
        self.easy_coords = (241, 180, 470, 230)
        self.medium_coords = (241, 265, 470, 315)
        self.hard_coords = (335, 350, 470, 410)
        self.back_coords = (335, 470, 565, 527)

    def run(self):
        global DIFFICULTY_LEVEL
        self.background.draw()
        
        if self.mouse.is_over_area(start_point=(self.easy_coords[0], self.easy_coords[1]), end_point=(self.easy_coords[2], self.easy_coords[3])) and self.mouse.is_button_pressed(1):
            DIFFICULTY_LEVEL = DIFFICULTY_EASY
        if self.mouse.is_over_area(start_point=(self.medium_coords[0], self.medium_coords[1]), end_point=(self.medium_coords[2], self.medium_coords[3])) and self.mouse.is_button_pressed(1):
            DIFFICULTY_LEVEL = DIFFICULTY_MEDIUM
        if self.mouse.is_over_area(start_point=(self.hard_coords[0], self.hard_coords[1]), end_point=(self.hard_coords[2], self.hard_coords[3])) and self.mouse.is_button_pressed(1):
            DIFFICULTY_LEVEL = DIFFICULTY_HARD
            
        if self.mouse.is_over_area(start_point=(self.back_coords[0], self.back_coords[1]), end_point=(self.back_coords[2], self.back_coords[3])) and self.mouse.is_button_pressed(1):
            return GAME_STATE_MENU
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_DIFFICULTY

class Ranking:
    """Tela de exibição do Ranking."""
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.titulo = Sprite(RANKING_TITLE_PATH)
        self.titulo.set_position(janela.width/2 - self.titulo.width/2, 25)
        self.scores = self._load_scores()

    def _load_scores(self):
        try:
            with open(RANKING_FILE, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return []
        
        scores_data = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 3:
                name, difficulty, score = parts
                try:
                    scores_data.append({'name': name, 'difficulty': difficulty, 'score': int(score)})
                except ValueError:
                    continue
        
        return sorted(scores_data, key=lambda x: x['score'], reverse=True)

    def run(self):
        self.titulo.draw()
        
        if not self.scores:
            self.janela.draw_text("Nenhuma pontuação registrada.", 200, 150, size=FONT_SIZE_LARGE, color=FONT_COLOR)
        else:
            for i, entry in enumerate(self.scores[:5]):
                text = f"{i+1}º {entry['name']} - {entry['score']} pts ({entry['difficulty']})"
                self.janela.draw_text(text, 150, 120 + i * 60, size=FONT_SIZE_LARGE, color=FONT_COLOR)

        self.janela.draw_text("Pressione ESC para voltar ao Menu", 250, 550, size=FONT_SIZE_SMALL, color=FONT_COLOR)
        
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_RANKING

class GameOverScreen:
    """Tela de Game Over para inserir o nome do jogador."""
    def __init__(self, janela, final_score):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.final_score = final_score
        self.player_name = ""
        self.cursor_timer = 0
        self.show_cursor = True
        self.last_key_press_time = 0
        self.key_repeat_delay = 0.1

    def _save_score(self):
        if not self.player_name:
            return
            
        diff_map = {DIFFICULTY_EASY: "Facil", DIFFICULTY_MEDIUM: "Medio", DIFFICULTY_HARD: "Dificil"}
        difficulty_str = diff_map.get(DIFFICULTY_LEVEL, "Desconhecido")
        
        new_entry = f"{self.player_name.replace(' ', '_')} {difficulty_str} {int(self.final_score)}\n"
        
        try:
            with open(RANKING_FILE, 'a') as f:
                f.write(new_entry)
        except IOError:
            print(f"Erro: Não foi possível escrever no arquivo {RANKING_FILE}")

    def run(self):
        dt = self.janela.delta_time()
        self.cursor_timer += dt
        self.last_key_press_time -= dt

        if self.cursor_timer > 0.4:
            self.show_cursor = not self.show_cursor
            self.cursor_timer = 0
            
        if self.last_key_press_time <= 0:
            for key in string.ascii_lowercase:
                if self.teclado.key_pressed(key) and len(self.player_name) < 10:
                    self.player_name += key.upper()
                    self.last_key_press_time = self.key_repeat_delay
                    break
            
            if self.teclado.key_pressed("BACKSPACE"):
                self.player_name = self.player_name[:-1]
                self.last_key_press_time = self.key_repeat_delay

            if self.teclado.key_pressed("ENTER") and self.player_name:
                self._save_score()
                return GAME_STATE_RANKING

        self.janela.draw_text("GAME OVER", self.janela.width/2 - 150, 150, size=60, color=(200, 0, 0), bold=True)
        self.janela.draw_text(f"PONTUAÇÃO FINAL: {int(self.final_score)}", self.janela.width/2 - 200, 250, size=FONT_SIZE_LARGE, color=FONT_COLOR)
        self.janela.draw_text("DIGITE SEU NOME:", self.janela.width/2 - 140, 350, size=FONT_SIZE_MEDIUM, color=FONT_COLOR)
        
        name_text = self.player_name
        if self.show_cursor:
            name_text += "_"
            
        self.janela.draw_text(name_text, self.janela.width/2 - (len(name_text)*12), 400, size=FONT_SIZE_LARGE, color=(255, 255, 0))
        self.janela.draw_text("Pressione ENTER para confirmar", self.janela.width/2 - 190, 500, size=FONT_SIZE_SMALL, color=FONT_COLOR)

        return GAME_STATE_GAME_OVER

# --- Função Principal e Loop do Jogo ---

def main():
    """Função principal que inicializa e executa o jogo."""
    global GAME_CURRENT_STATE
    
    janela = Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    janela.set_title(GAME_TITLE)

    assets = AssetManager()
    assets.set_volume(0.03)

    menu_screen = Menu(janela)
    difficulty_screen = Dificuldade(janela)
    ranking_screen = Ranking(janela)
    game_screen = None
    game_over_screen = None
    
    final_score = 0

    while GAME_CURRENT_STATE != GAME_STATE_EXIT:
        janela.set_background_color(BACKGROUND_COLOR)
        
        # ALTERAÇÃO: Lógica de música simplificada para tocar continuamente
        if not assets.background_music.is_playing():
            assets.background_music.play()
        
        if GAME_CURRENT_STATE == GAME_STATE_MENU:
            GAME_CURRENT_STATE = menu_screen.run()
            if GAME_CURRENT_STATE == GAME_STATE_PLAYING:
                game_screen = Jogar(janela, assets, DIFFICULTY_LEVEL)
        
        elif GAME_CURRENT_STATE == GAME_STATE_PLAYING:
            if game_screen:
                next_state, score = game_screen.run()
                if next_state != GAME_STATE_PLAYING:
                    final_score = score
                    GAME_CURRENT_STATE = next_state
                    game_screen = None
        
        elif GAME_CURRENT_STATE == GAME_STATE_DIFFICULTY:
            GAME_CURRENT_STATE = difficulty_screen.run()

        elif GAME_CURRENT_STATE == GAME_STATE_RANKING:
            GAME_CURRENT_STATE = ranking_screen.run()
        
        elif GAME_CURRENT_STATE == GAME_STATE_GAME_OVER:
            if not game_over_screen:
                game_over_screen = GameOverScreen(janela, final_score)
            GAME_CURRENT_STATE = game_over_screen.run()
            if GAME_CURRENT_STATE != GAME_STATE_GAME_OVER:
                game_over_screen = None
                ranking_screen = Ranking(janela)

        janela.update()

if __name__ == "__main__":
    main()