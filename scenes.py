import string
import random
import pygame
from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.animation import *
from PPlay.mouse import *

from constants import *
from entities import Jogador, Inimigos, PowerUp

# --- CLASSE DE BOTÃO REUTILIZÁVEL ---
class Button:
    def __init__(self, text, x, y, width=250, height=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.Font(FONT_PATH, 30)

    def draw(self, janela, mouse):
        self.is_hovered = self.rect.collidepoint(mouse.get_position())
        bg_color = DARK_CYAN if self.is_hovered else CYAN
        pygame.draw.rect(janela.screen, bg_color, self.rect, border_radius=10)
        
        text_color = WHITE if self.is_hovered else BACKGROUND_COLOR
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        janela.screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_is_new_click):
        return self.is_hovered and mouse_is_new_click

class Jogar:
    # ... (a classe Jogar não foi alterada) ...
    def __init__(self, janela, assets, settings):
        self.janela = janela
        self.assets = assets
        self.settings = settings
        self.teclado = janela.get_keyboard()
        self.pontuacao = 0
        self.nivel = 1
        self.jogador = Jogador(janela, assets, settings)
        self.inimigos = Inimigos(janela, self.nivel, settings)
        self.active_powerups = []
        self.active_explosions = []
        
    def _check_collisions(self):
        for linha in self.inimigos.matrizInimigos:
            for i, inimigo in reversed(list(enumerate(linha))):
                for j, tiro in reversed(list(enumerate(self.jogador.listaTiros))):
                    if tiro.collided(inimigo):
                        self.pontuacao += SCORE_HIT_ENEMY_BASE * self.settings["score_multiplier"]
                        self._create_explosion(inimigo.x, inimigo.y)
                        self.assets.enemy_explosion.play()
                        
                        if random.random() < self.settings["powerup_drop_chance"]:
                            p_type = random.choice([POWERUP_TYPE_SHIELD, POWERUP_TYPE_FAST_SHOT])
                            self.active_powerups.append(PowerUp(inimigo.x, inimigo.y, p_type))

                        linha.pop(i)
                        self.jogador.listaTiros.pop(j)
                        break
        
        for i, tiro_inimigo in reversed(list(enumerate(self.inimigos.listaTiros))):
            if tiro_inimigo.collided(self.jogador.player):
                self.inimigos.listaTiros.pop(i)
                self._handle_player_hit()
                break

        for i, powerup in reversed(list(enumerate(self.active_powerups))):
            if powerup.collided(self.jogador.player):
                if powerup.type_id == POWERUP_TYPE_SHIELD: self.jogador.has_shield = True; self.jogador.shield_timer = POWERUP_SHIELD_DURATION
                else: self.jogador.is_fast_shooting = True; self.jogador.fast_shot_timer = POWERUP_FAST_SHOT_DURATION
                self.active_powerups.pop(i)
    
    def _handle_player_hit(self):
        if self.jogador.has_shield:
            self.jogador.has_shield = False
            return
            
        self._create_explosion(self.jogador.player.x, self.jogador.player.y)
        self.assets.player_hit.play()
        self.jogador.vidas -= 1
        
        if self.jogador.vidas > 0:
            self.jogador.set_initial_pos()
        else:
            self.jogador.player.set_position(-1000, -1000)

    def _create_explosion(self, x, y):
        explosion = Animation(PLAYER_DEATH_ANIM_PATH, 12, loop=False)
        explosion.set_total_duration(500)
        explosion.set_position(x, y)
        self.active_explosions.append(explosion)

    def _update_and_draw_effects(self, dt):
        self.active_explosions = [e for e in self.active_explosions if e.get_curr_frame() < e.get_final_frame() - 1]
        for e in self.active_explosions:
            e.update(); e.draw()
            
        self.active_powerups = [p for p in self.active_powerups if p.y < self.janela.height]
        for p in self.active_powerups:
            p.run(dt)

    def _draw_hud(self):
        table_color = CYAN
        border_width = 2
        table_rect = pygame.Rect(5, 5, WINDOW_WIDTH - 10, 60)
        
        col_width = table_rect.width // 4
        
        pygame.draw.rect(self.janela.screen, table_color, table_rect, border_width, border_radius=5)
        for i in range(1, 4):
            div_x = table_rect.x + col_width * i
            pygame.draw.line(self.janela.screen, table_color, (div_x, table_rect.y), (div_x, table_rect.y + table_rect.height), border_width)

        label_y = table_rect.y + 8
        value_y = table_rect.y + 30
        label_color = GRAY
        value_color = WHITE

        self.janela.draw_text("VIDAS", 95, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(self.jogador.vidas), 110, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("NÍVEL", 315, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(self.nivel), 332, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("DIFICULDADE", 505, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(self.settings['name'].upper(), 530, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("PONTOS", 750, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(int(self.pontuacao)), 760, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)

    def _check_game_over_conditions(self):
        if self.jogador.vidas <= 0: return True
        if self.jogador.vidas > 0:
            for linha in self.inimigos.matrizInimigos:
                for inimigo in linha:
                    if (inimigo.y + inimigo.height) >= self.jogador.player.y: return True
        return False

    def _level_up(self):
        self.pontuacao += SCORE_PASS_LEVEL_BASE * self.nivel * self.settings["score_multiplier"]
        self.nivel += 1
        self.jogador.listaTiros.clear()
        self.active_powerups.clear()
        self.inimigos = Inimigos(self.janela, self.nivel, self.settings)

    def run(self):
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU, self.pontuacao
            
        dt = self.janela.delta_time()
        self.jogador.run()
        self.inimigos.run()
        self._check_collisions()
        self._update_and_draw_effects(dt)
        self._draw_hud()

        if self._check_game_over_conditions():
            return GAME_STATE_GAME_OVER, self.pontuacao
            
        if self.inimigos.quantidade_total == 0:
            self._level_up()

        return GAME_STATE_PLAYING, self.pontuacao

class Menu:
    # ... (a classe Menu não foi alterada) ...
    def __init__(self, janela):
        self.janela = janela
        self.background = GameImage(MENU_BACKGROUND_PATH)
        self.mouse = Mouse()
        self.play_coords = (335, 180, 567, 230)
        self.diff_coords = (335, 265, 567, 315)
        self.rank_coords = (335, 350, 567, 400)
        self.exit_coords = (335, 435, 567, 485)

    def run(self, is_new_click):
        self.background.draw()
        
        if is_new_click:
            if self.mouse.is_over_area(start_point=(self.play_coords[0], self.play_coords[1]), end_point=(self.play_coords[2], self.play_coords[3])):
                return GAME_STATE_PLAYING
            if self.mouse.is_over_area(start_point=(self.diff_coords[0], self.diff_coords[1]), end_point=(self.diff_coords[2], self.diff_coords[3])):
                return GAME_STATE_DIFFICULTY
            if self.mouse.is_over_area(start_point=(self.rank_coords[0], self.rank_coords[1]), end_point=(self.rank_coords[2], self.rank_coords[3])):
                return GAME_STATE_RANKING
            if self.mouse.is_over_area(start_point=(self.exit_coords[0], self.exit_coords[1]), end_point=(self.exit_coords[2], self.exit_coords[3])):
                return GAME_STATE_EXIT
                
        return GAME_STATE_MENU

class Dificuldade:
    # ... (a classe Dificuldade não foi alterada) ...
    def __init__(self, janela):
        self.janela = janela
        self.background = GameImage(DIFFICULTY_BACKGROUND_PATH)
        self.mouse = Mouse()
        self.teclado = janela.get_keyboard()
        self.easy_coords = (241, 180, 470, 230)
        self.medium_coords = (241, 265, 470, 315)
        self.hard_coords = (335, 350, 470, 410)

    def run(self, is_new_click, game_state):
        self.background.draw()

        if is_new_click:
            if self.mouse.is_over_area(start_point=(self.easy_coords[0], self.easy_coords[1]), end_point=(self.easy_coords[2], self.easy_coords[3])):
                game_state["difficulty"] = DIFFICULTY_EASY
                return GAME_STATE_MENU
            if self.mouse.is_over_area(start_point=(self.medium_coords[0], self.medium_coords[1]), end_point=(self.medium_coords[2], self.medium_coords[3])):
                game_state["difficulty"] = DIFFICULTY_MEDIUM
                return GAME_STATE_MENU
            if self.mouse.is_over_area(start_point=(self.hard_coords[0], self.hard_coords[1]), end_point=(self.hard_coords[2], self.hard_coords[3])):
                game_state["difficulty"] = DIFFICULTY_HARD
                return GAME_STATE_MENU
            
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_DIFFICULTY

# --- CLASSE RANKING TOTALMENTE REFORMULADA ---
class Ranking:
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.mouse = Mouse()
        self.scores = self._load_scores()
        
        # Elementos visuais
        self.font_title = pygame.font.Font(FONT_PATH, 70)
        self.font_header = pygame.font.Font(FONT_PATH, 24)
        self.font_entry = pygame.font.Font(FONT_PATH, 28)
        self.back_button = Button("Voltar", WINDOW_WIDTH / 2 - 125, 520)

    def _load_scores(self):
        try:
            with open(RANKING_FILE, 'r') as f: lines = f.readlines()
        except FileNotFoundError: return []
        
        scores_data = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 3:
                name, difficulty, score = parts
                try: scores_data.append({'name': name, 'difficulty': difficulty, 'score': int(score)})
                except ValueError: continue
        return sorted(scores_data, key=lambda x: x['score'], reverse=True)

    def run(self, is_new_click):
        # Título
        title_surf = self.font_title.render("RANKING", True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 80))
        self.janela.screen.blit(title_surf, title_rect)
        
        # Cabeçalho da Tabela
        header_y = 180
        pygame.draw.line(self.janela.screen, GRAY, (100, header_y + 30), (WINDOW_WIDTH - 100, header_y + 30), 2)
        self.janela.draw_text("POS", 110, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("NOME", 220, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("PONTOS", 470, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("DIFICULDADE", 650, header_y, size=24, color=GRAY, font_name=FONT_PATH)

        # Entradas do Ranking
        if not self.scores:
            self.janela.draw_text("Nenhuma pontuacao registrada.", 220, 280, size=30, color=WHITE, font_name=FONT_PATH)
        else:
            for i, entry in enumerate(self.scores[:5]):
                entry_y = 240 + i * 50
                color = CYAN if i == 0 else WHITE

                # Usando pygame.font para alinhar melhor
                pos_surf = self.font_entry.render(f"{i+1}.", True, color)
                self.janela.screen.blit(pos_surf, (120, entry_y))

                name_surf = self.font_entry.render(entry['name'], True, color)
                self.janela.screen.blit(name_surf, (220, entry_y))
                
                score_surf = self.font_entry.render(str(entry['score']), True, color)
                self.janela.screen.blit(score_surf, (470, entry_y))

                diff_surf = self.font_entry.render(entry['difficulty'], True, color)
                self.janela.screen.blit(diff_surf, (650, entry_y))

        # Botão de Voltar
        self.back_button.draw(self.janela, self.mouse)
        if self.back_button.is_clicked(is_new_click) or self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_RANKING

class GameOverScreen:
    # ... (a classe GameOverScreen não foi alterada) ...
    def __init__(self, janela, final_score, difficulty_level):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.final_score = final_score
        self.difficulty_level = difficulty_level
        self.player_name = ""
        self.cursor_timer = 0
        self.show_cursor = True
        
        self.font_title = pygame.font.Font(FONT_PATH, 80)
        self.font_score = pygame.font.Font(FONT_PATH, 40)
        self.font_label = pygame.font.Font(FONT_PATH, 28)
        self.font_input = pygame.font.Font(FONT_PATH, 32)
        self.font_confirm = pygame.font.Font(FONT_PATH, 25)

        self.keys_to_check = list(string.ascii_uppercase + string.digits) + ["BACKSPACE", "ENTER"]
        self.last_key_state = {key: False for key in self.keys_to_check}

    def _save_score(self):
        if not self.player_name: return
        difficulty_name = DIFFICULTY_SETTINGS[self.difficulty_level]["name"]
        new_entry = f"{self.player_name.replace(' ', '_')} {difficulty_name} {int(self.final_score)}\n"
        
        try:
            with open(RANKING_FILE, 'a') as f: f.write(new_entry)
        except IOError:
            print(f"Erro: Não foi possível escrever no arquivo {RANKING_FILE}")

    def run(self):
        for key in self.keys_to_check:
            key_is_pressed = self.teclado.key_pressed(key)
            if key_is_pressed and not self.last_key_state[key]:
                if key == "BACKSPACE":
                    self.player_name = self.player_name[:-1]
                elif key == "ENTER":
                    if self.player_name:
                        self._save_score()
                        return GAME_STATE_RANKING
                elif len(self.player_name) < 10:
                    self.player_name += key
            self.last_key_state[key] = key_is_pressed

        self.cursor_timer += self.janela.delta_time()
        if self.cursor_timer > 0.4:
            self.show_cursor = not self.show_cursor
            self.cursor_timer = 0
            
        title_surf = self.font_title.render("GAME OVER", True, (200, 0, 0))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 150))
        self.janela.screen.blit(title_surf, title_rect)

        score_surf = self.font_score.render(f"PONTUAÇÃO FINAL: {int(self.final_score)}", True, WHITE)
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH / 2, 250))
        self.janela.screen.blit(score_surf, score_rect)

        label_surf = self.font_label.render("DIGITE SEU NOME:", True, GRAY)
        label_rect = label_surf.get_rect(center=(WINDOW_WIDTH / 2, 330))
        self.janela.screen.blit(label_surf, label_rect)

        input_box_rect = pygame.Rect((WINDOW_WIDTH / 2) - 200, 360, 400, 50)
        pygame.draw.rect(self.janela.screen, GRAY, input_box_rect, 2, border_radius=5)

        input_text = self.player_name + ("|" if self.show_cursor else "")
        input_surf = self.font_input.render(input_text, True, (255, 255, 0))
        input_rect = input_surf.get_rect(center=input_box_rect.center)
        self.janela.screen.blit(input_surf, input_rect)

        confirm_surf = self.font_confirm.render("Pressione ENTER para confirmar", True, WHITE)
        confirm_rect = confirm_surf.get_rect(center=(WINDOW_WIDTH / 2, 450))
        self.janela.screen.blit(confirm_surf, confirm_rect)
        
        return GAME_STATE_GAME_OVER