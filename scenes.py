import string
import random
import pygame
from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.animation import *
from PPlay.mouse import *

from constants import *
from entities import Jogador, Inimigos, PowerUp, Boss

class Button:
    """Classe para criar botões de menu clicáveis e estilizados."""
    def __init__(self, text, x, y, width=250, height=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.Font(FONT_PATH, 30)

    def draw(self, janela, mouse):
        self.is_hovered = self.rect.collidepoint(mouse.get_position())
        bg_color = DARK_CYAN if self.is_hovered else CYAN
        pygame.draw.rect(janela.screen, bg_color, self.rect, border_radius=10)
        
        text_color = BACKGROUND_COLOR
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        janela.screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_is_new_click):
        return self.is_hovered and mouse_is_new_click

class Jogar:
    """Cena principal do jogo, onde toda a ação acontece."""
    def __init__(self, janela, assets, settings):
        self.janela = janela
        self.assets = assets
        self.settings = settings
        self.teclado = janela.get_keyboard()
        self.pontuacao = 0
        self.nivel = 1
        self.jogador = Jogador(janela, assets, settings)
        self.active_powerups = []
        self.active_explosions = []
        
        # Atributos para o tremor de tela
        self.is_shaking = False
        self.shake_duration = 0.2
        self.shake_intensity = 4
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        self._prepare_next_level()
        
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
            if tiro_inimigo.collided_perfect(self.jogador.player):
                self.inimigos.listaTiros.pop(i)
                self._handle_player_hit()
                break

        for i, powerup in reversed(list(enumerate(self.active_powerups))):
            if powerup.collided(self.jogador.player):
                if powerup.type_id == POWERUP_TYPE_SHIELD: self.jogador.has_shield = True; self.jogador.shield_timer = POWERUP_SHIELD_DURATION
                else: self.jogador.is_fast_shooting = True; self.jogador.fast_shot_timer = POWERUP_FAST_SHOT_DURATION
                self.active_powerups.pop(i)

    def _check_boss_collisions(self):
        if not self.boss: return

        for j, tiro in reversed(list(enumerate(self.jogador.listaTiros))):
            if tiro.collided_perfect(self.boss.sprite):
                self.boss.health -= 1
                self.pontuacao += SCORE_HIT_BOSS_BASE * self.settings["score_multiplier"]
                self._create_explosion(tiro.x, tiro.y)
                self.jogador.listaTiros.pop(j)

        for i, tiro_inimigo in reversed(list(enumerate(self.boss.listaTiros))):
            if tiro_inimigo.collided_perfect(self.jogador.player):
                self.boss.listaTiros.pop(i)
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
            
        self.is_shaking = True
        self.shake_timer = self.shake_duration

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

    def _update_and_draw_effects(self, dt, offset_x=0, offset_y=0):
        # Explosões
        self.active_explosions = [e for e in self.active_explosions if e.get_curr_frame() < e.get_final_frame() - 1]
        for e in self.active_explosions:
            e.update()
            e.x += offset_x
            e.y += offset_y
            e.draw()
            e.x -= offset_x
            e.y -= offset_y
            
        # Power-ups
        self.active_powerups = [p for p in self.active_powerups if p.y < self.janela.height]
        for p in self.active_powerups:
            p.run(dt, offset_x, offset_y)

    def _draw_hud(self, offset_x=0, offset_y=0):
        table_color = CYAN
        border_width = 2
        
        table_rect = pygame.Rect(5 + offset_x, 5 + offset_y, WINDOW_WIDTH - 10, 60)
        
        col_width = table_rect.width // 4
        
        pygame.draw.rect(self.janela.screen, table_color, table_rect, border_width, border_radius=5)
        for i in range(1, 4):
            div_x = table_rect.x + col_width * i
            pygame.draw.line(self.janela.screen, table_color, (div_x, table_rect.y), (div_x, table_rect.y + table_rect.height), border_width)

        label_y = table_rect.y + 8
        value_y = table_rect.y + 30
        label_color = GRAY
        value_color = WHITE

        self.janela.draw_text("VIDAS", 95 + offset_x, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(self.jogador.vidas), 110 + offset_x, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("NÍVEL", 315 + offset_x, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(self.nivel), 332 + offset_x, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("DIFICULDADE", 505 + offset_x, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(self.settings['name'].upper(), 530 + offset_x, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)
        self.janela.draw_text("PONTOS", 750 + offset_x, label_y, size=20, color=label_color, font_name=FONT_PATH)
        self.janela.draw_text(str(int(self.pontuacao)), 760 + offset_x, value_y, size=24, color=value_color, bold=True, font_name=FONT_PATH)

        if self.is_boss_fight and self.boss:
            bar_w, bar_h, bar_x, bar_y = 400, 20, (WINDOW_WIDTH - 400) / 2, 75
            health_perc = self.boss.health / self.boss.max_health if self.boss.max_health > 0 else 0
            current_health_w = bar_w * health_perc
            
            health_bar_bg_rect = pygame.Rect(bar_x + offset_x, bar_y + offset_y, bar_w, bar_h)
            health_bar_fg_rect = pygame.Rect(bar_x + offset_x, bar_y + offset_y, current_health_w, bar_h)

            pygame.draw.rect(self.janela.screen, (100,0,0), health_bar_bg_rect, border_radius=5)
            pygame.draw.rect(self.janela.screen, (255,0,0), health_bar_fg_rect, border_radius=5)
            pygame.draw.rect(self.janela.screen, WHITE, health_bar_bg_rect, 2, border_radius=5)

    def _check_game_over_conditions(self):
        if self.jogador.vidas <= 0 and not self.is_shaking: return True
        if not self.is_boss_fight:
            if self.jogador.vidas > 0:
                for linha in self.inimigos.matrizInimigos:
                    for inimigo in linha:
                        if (inimigo.y + inimigo.height) >= self.jogador.player.y: return True
        return False

    def _prepare_next_level(self):
        self.jogador.listaTiros.clear()
        self.active_powerups.clear()
        self.boss = None
        self.is_boss_fight = False
        self.inimigos = Inimigos(self.janela, self.nivel, self.settings)

        if self.nivel % 5 == 0:
            self.is_boss_fight = True
            self.boss = Boss(self.janela, self.nivel, self.settings)
            self.inimigos.matrizInimigos.clear() 

    def _level_up(self):
        self.pontuacao += SCORE_PASS_LEVEL_BASE * self.nivel * self.settings["score_multiplier"]
        self.nivel += 1
        self._prepare_next_level()

    def run(self):
        dt = self.janela.delta_time()

        if self.is_shaking:
            self.shake_timer -= dt
            if self.shake_timer > 0:
                self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            else:
                self.is_shaking = False
                self.shake_offset_x = 0
                self.shake_offset_y = 0
        
        if self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU, self.pontuacao
            
        self.jogador.run(self.shake_offset_x, self.shake_offset_y)
        
        if self.is_boss_fight:
            if self.boss:
                self.boss.run(dt, self.shake_offset_x, self.shake_offset_y)
                self._check_boss_collisions()
                if self.boss.health <= 0:
                    self.pontuacao += SCORE_BOSS_DEFEAT_BASE * self.nivel * self.settings["score_multiplier"]
                    self._create_explosion(self.boss.sprite.x, self.boss.sprite.y)
                    self.assets.enemy_explosion.play()
                    self._level_up()
        else:
            self.inimigos.run(self.shake_offset_x, self.shake_offset_y)
            self._check_collisions()
            if self.inimigos.quantidade_total == 0:
                self._level_up()
        
        self._update_and_draw_effects(dt, self.shake_offset_x, self.shake_offset_y)
        self._draw_hud(self.shake_offset_x, self.shake_offset_y)

        if self._check_game_over_conditions():
            return GAME_STATE_GAME_OVER, self.pontuacao
            
        return GAME_STATE_PLAYING, self.pontuacao

class Menu:
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.font_title = pygame.font.Font(FONT_PATH, 70)
        
        btn_x = (WINDOW_WIDTH / 2) - 125
        self.buttons = [
            Button("Jogar", btn_x, 200),
            Button("Dificuldade", btn_x, 270),
            Button("Ranking", btn_x, 340),
            Button("Sair", btn_x, 410)
        ]

    def run(self, is_new_click):
        title_surf = self.font_title.render(GAME_TITLE, True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 80))
        self.janela.screen.blit(title_surf, title_rect)
        
        for btn in self.buttons:
            btn.draw(self.janela, self.mouse)
            
        if self.buttons[0].is_clicked(is_new_click): return GAME_STATE_PLAYING
        if self.buttons[1].is_clicked(is_new_click): return GAME_STATE_DIFFICULTY
        if self.buttons[2].is_clicked(is_new_click): return GAME_STATE_RANKING
        if self.buttons[3].is_clicked(is_new_click): return GAME_STATE_EXIT
                
        return GAME_STATE_MENU

class Dificuldade:
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.teclado = janela.get_keyboard()
        self.font_title = pygame.font.Font(FONT_PATH, 70)

        btn_x = (WINDOW_WIDTH / 2) - 125
        self.buttons = [
            Button("Facil", btn_x, 200),
            Button("Medio", btn_x, 270),
            Button("Dificil", btn_x, 340),
            Button("Voltar", btn_x, 430)
        ]
        
    def run(self, is_new_click, game_state):
        title_surf = self.font_title.render("DIFICULDADE", True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 80))
        self.janela.screen.blit(title_surf, title_rect)

        for btn in self.buttons:
            btn.draw(self.janela, self.mouse)

        if self.buttons[0].is_clicked(is_new_click):
            game_state["difficulty"] = DIFFICULTY_EASY
            return GAME_STATE_MENU
        if self.buttons[1].is_clicked(is_new_click):
            game_state["difficulty"] = DIFFICULTY_MEDIUM
            return GAME_STATE_MENU
        if self.buttons[2].is_clicked(is_new_click):
            game_state["difficulty"] = DIFFICULTY_HARD
            return GAME_STATE_MENU
        if self.buttons[3].is_clicked(is_new_click) or self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_DIFFICULTY

class Ranking:
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.mouse = Mouse()
        self.scores = self._load_scores()
        
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
        title_surf = self.font_title.render("RANKING", True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 80))
        self.janela.screen.blit(title_surf, title_rect)
        
        header_y = 180
        pygame.draw.line(self.janela.screen, GRAY, (100, header_y + 30), (WINDOW_WIDTH - 100, header_y + 30), 2)
        self.janela.draw_text("POS", 110, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("NOME", 220, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("PONTOS", 470, header_y, size=24, color=GRAY, font_name=FONT_PATH)
        self.janela.draw_text("DIFICULDADE", 650, header_y, size=24, color=GRAY, font_name=FONT_PATH)

        if not self.scores:
            self.janela.draw_text("Nenhuma pontuacao registrada.", 220, 280, size=30, color=WHITE, font_name=FONT_PATH)
        else:
            for i, entry in enumerate(self.scores[:5]):
                entry_y = 240 + i * 50
                color = CYAN if i == 0 else WHITE

                pos_surf = self.font_entry.render(f"{i+1}.", True, color)
                self.janela.screen.blit(pos_surf, (120, entry_y))
                name_surf = self.font_entry.render(entry['name'], True, color)
                self.janela.screen.blit(name_surf, (220, entry_y))
                score_surf = self.font_entry.render(str(entry['score']), True, color)
                self.janela.screen.blit(score_surf, (470, entry_y))
                diff_surf = self.font_entry.render(entry['difficulty'], True, color)
                self.janela.screen.blit(diff_surf, (650, entry_y))

        self.back_button.draw(self.janela, self.mouse)
        if self.back_button.is_clicked(is_new_click) or self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_RANKING

class GameOverScreen:
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