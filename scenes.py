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
    """Cria um botão de menu clicável e estilizado."""
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
    """Cena principal do jogo, onde toda a ação e lógica de gameplay acontecem."""
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

        # Atributos para o menu de pausa
        self.is_paused = False
        self.esc_was_pressed = False
        btn_x = (WINDOW_WIDTH / 2) - 125
        self.pause_buttons = [
            Button("Continuar", btn_x, 220),
            Button("Reiniciar", btn_x, 290),
            Button("Menu", btn_x, 360)
        ]
        
        self._prepare_next_level()
        
    def _check_collisions(self):
        """Verifica e processa todas as colisões do jogo (tiros, power-ups, etc)."""
        # Tiros do jogador vs. Inimigos
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
        
        # Tiros dos inimigos vs. Jogador
        for i, tiro_inimigo in reversed(list(enumerate(self.inimigos.listaTiros))):
            if tiro_inimigo.collided_perfect(self.jogador.player):
                self.inimigos.listaTiros.pop(i)
                self._handle_player_hit()
                break

        # Power-ups vs. Jogador
        for i, powerup in reversed(list(enumerate(self.active_powerups))):
            if powerup.collided(self.jogador.player):
                if powerup.type_id == POWERUP_TYPE_SHIELD: self.jogador.has_shield = True; self.jogador.shield_timer = POWERUP_SHIELD_DURATION
                else: self.jogador.is_fast_shooting = True; self.jogador.fast_shot_timer = POWERUP_FAST_SHOT_DURATION
                self.active_powerups.pop(i)

    def _check_boss_collisions(self):
        """Verifica e processa colisões específicas da batalha contra o chefe."""
        if not self.boss: return

        # Tiros do jogador vs. Chefe
        for j, tiro in reversed(list(enumerate(self.jogador.listaTiros))):
            if tiro.collided_perfect(self.boss.sprite):
                self.boss.health -= 1
                self.pontuacao += SCORE_HIT_BOSS_BASE * self.settings["score_multiplier"]
                self._create_explosion(tiro.x, tiro.y)
                self.jogador.listaTiros.pop(j)

        # Tiros do chefe vs. Jogador
        for i, tiro_inimigo in reversed(list(enumerate(self.boss.listaTiros))):
            if tiro_inimigo.collided_perfect(self.jogador.player):
                self.boss.listaTiros.pop(i)
                self._handle_player_hit()
                break
    
    def _handle_player_hit(self):
        """Processa o que acontece quando o jogador é atingido."""
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
        """Cria uma animação de explosão em uma dada coordenada."""
        explosion = Animation(PLAYER_DEATH_ANIM_PATH, 12, loop=False)
        explosion.set_total_duration(500)
        explosion.set_position(x, y)
        self.active_explosions.append(explosion)

    # --- MÉTODO SEPARADO PARA ATUALIZAÇÃO ---
    def _update_effects(self, dt):
        """Atualiza a lógica de efeitos visuais como explosões e power-ups."""
        self.active_explosions = [e for e in self.active_explosions if e.get_curr_frame() < e.get_final_frame() - 1]
        for e in self.active_explosions:
            e.update()
            
        self.active_powerups = [p for p in self.active_powerups if p.y < self.janela.height]
        for p in self.active_powerups:
            p.update(dt) # <--- CORRIGIDO: usa .update()

    # --- MÉTODO SEPARADO PARA DESENHO ---
    def _draw_effects(self, offset_x=0, offset_y=0):
        """Desenha efeitos visuais como explosões e power-ups."""
        from entities import draw_with_offset
        for e in self.active_explosions:
            draw_with_offset(e, offset_x, offset_y)
            
        for p in self.active_powerups:
            p.draw(offset_x, offset_y) # <--- CORRIGIDO: usa .draw()

    def _draw_pause_menu(self):
        """Desenha a sobreposição escura e os botões do menu de pausa."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.janela.screen.blit(overlay, (0, 0))
        mouse = Mouse()
        for btn in self.pause_buttons:
            btn.draw(self.janela, mouse)

    def _handle_pause_input(self, is_new_click):
        """Verifica cliques nos botões de pausa e retorna o estado de jogo apropriado."""
        if self.pause_buttons[0].is_clicked(is_new_click):
            self.is_paused = False
        if self.pause_buttons[1].is_clicked(is_new_click):
            return GAME_STATE_RESTART, 0
        if self.pause_buttons[2].is_clicked(is_new_click):
            return GAME_STATE_MENU, self.pontuacao
        return None, None

    def _draw_hud(self, offset_x=0, offset_y=0):
        """Desenha a interface do usuário (vidas, pontos, nível, etc.)."""
        table_color = CYAN
        border_width = 2
        table_rect = pygame.Rect(5 + offset_x, 5 + offset_y, WINDOW_WIDTH - 10, 60)
        col_width = table_rect.width // 4
        
        pygame.draw.rect(self.janela.screen, table_color, table_rect, border_width, border_radius=5)
        for i in range(1, 4):
            div_x = table_rect.x + col_width * i
            pygame.draw.line(self.janela.screen, table_color, (div_x, table_rect.y), (div_x, table_rect.y + table_rect.height), border_width)

        label_y, value_y = table_rect.y + 8, table_rect.y + 30
        label_color, value_color = GRAY, WHITE

        # Desenha os textos do HUD
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
        """Verifica as condições de fim de jogo."""
        if self.jogador.vidas <= 0 and not self.is_shaking: return True
        if not self.is_boss_fight:
            if self.jogador.vidas > 0:
                for linha in self.inimigos.matrizInimigos:
                    for inimigo in linha:
                        if (inimigo.y + inimigo.height) >= self.jogador.player.y: return True
        return False

    def _prepare_next_level(self):
        """Prepara o próximo nível, criando inimigos normais ou um chefe."""
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
        """Avança para o próximo nível e atualiza a pontuação."""
        self.pontuacao += SCORE_PASS_LEVEL_BASE * self.nivel * self.settings["score_multiplier"]
        self.nivel += 1
        self._prepare_next_level()

    def run(self, is_new_click):
        """Loop principal da cena de jogo, chamado a cada frame."""
        # --- Atualização de Estados (Pausa e Tremor) ---
        esc_is_pressed = self.teclado.key_pressed("ESC")
        if esc_is_pressed and not self.esc_was_pressed:
            self.is_paused = not self.is_paused
        self.esc_was_pressed = esc_is_pressed

        dt = self.janela.delta_time()
        if self.is_shaking:
            self.shake_timer -= dt
            if self.shake_timer > 0:
                self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            else:
                self.is_shaking = False
                self.shake_offset_x, self.shake_offset_y = 0, 0
        
        # --- Lógica de Atualização (Roda apenas se não estiver pausado) ---
        if not self.is_paused:
            self.jogador.update(dt)
            
            if self.is_boss_fight:
                if self.boss:
                    self.boss.update(dt)
                    self._check_boss_collisions()
                    if self.boss.health <= 0:
                        self.pontuacao += SCORE_BOSS_DEFEAT_BASE * self.nivel * self.settings["score_multiplier"]
                        self._create_explosion(self.boss.sprite.x, self.boss.sprite.y)
                        self.assets.enemy_explosion.play()
                        self._level_up()
            else:
                self.inimigos.update(dt)
                self._check_collisions()
                if self.inimigos.quantidade_total == 0:
                    self._level_up()
            
            self._update_effects(dt) # <--- CHAMADA CORRIGIDA
        
        # --- Lógica de Desenho (Sempre acontece) ---
        self.jogador.draw(self.shake_offset_x, self.shake_offset_y)
        if self.is_boss_fight:
            if self.boss: self.boss.draw(self.shake_offset_x, self.shake_offset_y)
        else:
            self.inimigos.draw(self.shake_offset_x, self.shake_offset_y)
        
        self._draw_effects(self.shake_offset_x, self.shake_offset_y) # <--- NOVA CHAMADA
        self._draw_hud(self.shake_offset_x, self.shake_offset_y)

        # Se pausado, desenha o menu de pausa por cima de tudo
        if self.is_paused:
            self._draw_pause_menu()
            next_scene, score = self._handle_pause_input(is_new_click)
            if next_scene:
                return next_scene, score

        # --- Verificação de Fim de Jogo ---
        if self._check_game_over_conditions():
            return GAME_STATE_GAME_OVER, self.pontuacao
            
        return GAME_STATE_PLAYING, self.pontuacao

class Menu:
    """Cena do Menu Principal."""
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.font_title = pygame.font.Font(FONT_PATH, 70)
        
        btn_x = (WINDOW_WIDTH / 2) - 125
        self.buttons = [
            Button("Jogar", btn_x, 200),
            Button("Como Jogar", btn_x, 270),
            Button("Dificuldade", btn_x, 340),
            Button("Ranking", btn_x, 410),
            Button("Sair", btn_x, 480)
        ]

    def run(self, is_new_click):
        title_surf = self.font_title.render(GAME_TITLE, True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 80))
        self.janela.screen.blit(title_surf, title_rect)
        
        for btn in self.buttons:
            btn.draw(self.janela, self.mouse)
            
        if self.buttons[0].is_clicked(is_new_click): return GAME_STATE_PLAYING
        if self.buttons[1].is_clicked(is_new_click): return GAME_STATE_HOW_TO_PLAY
        if self.buttons[2].is_clicked(is_new_click): return GAME_STATE_DIFFICULTY
        if self.buttons[3].is_clicked(is_new_click): return GAME_STATE_RANKING
        if self.buttons[4].is_clicked(is_new_click): return GAME_STATE_EXIT
                
        return GAME_STATE_MENU

class Dificuldade:
    """Cena de Seleção de Dificuldade."""
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.teclado = janela.get_keyboard()
        self.font_title = pygame.font.Font(FONT_PATH, 70)

        btn_x = (WINDOW_WIDTH / 2) - 125
        self.buttons = [
            Button("Fácil", btn_x, 200),
            Button("Médio", btn_x, 270),
            Button("Difícil", btn_x, 340),
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

class ComoJogar:
    """Cena que explica os controles e power-ups com um layout profissional."""
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.mouse = Mouse()
        
        self.font_title = pygame.font.Font(FONT_PATH, 60)
        self.font_header = pygame.font.Font(FONT_PATH, 32)
        self.font_text = pygame.font.Font(FONT_PATH, 24)
        
        self.back_button = Button("Voltar", WINDOW_WIDTH / 2 - 125, 520)

        self.shield_powerup_sprite = Sprite(POWERUP_SHIELD_PATH)
        self.fastshot_powerup_sprite = Sprite(POWERUP_FAST_SHOT_PATH)

    def run(self, is_new_click):
        RED = (255, 60, 60)
        
        title_surf = self.font_title.render("COMO JOGAR", True, CYAN)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, 70))
        self.janela.screen.blit(title_surf, title_rect)
        
        pygame.draw.line(self.janela.screen, GRAY, (100, 115), (WINDOW_WIDTH - 100, 115), 2)

        label_x = 180
        value_x = 450
        current_y = 150
        line_height = 40

        # --- Seção de Controles ---
        header_controles_surf = self.font_header.render("Controles", True, RED)
        header_controles_rect = header_controles_surf.get_rect(center=(WINDOW_WIDTH / 2, current_y))
        self.janela.screen.blit(header_controles_surf, header_controles_rect)
        current_y += 50

        self.janela.draw_text("Mover para a Esquerda:", label_x, current_y, font_name=FONT_PATH, size=24, color=GRAY)
        self.janela.draw_text("SETA ESQUERDA / A", value_x, current_y, font_name=FONT_PATH, size=24, color=WHITE)
        current_y += line_height

        self.janela.draw_text("Mover para a Direita:", label_x, current_y, font_name=FONT_PATH, size=24, color=GRAY)
        self.janela.draw_text("SETA DIREITA / D", value_x, current_y, font_name=FONT_PATH, size=24, color=WHITE)
        current_y += line_height

        self.janela.draw_text("Atirar:", label_x, current_y, font_name=FONT_PATH, size=24, color=GRAY)
        self.janela.draw_text("BARRA DE ESPAÇO", value_x, current_y, font_name=FONT_PATH, size=24, color=WHITE)
        current_y += 50
        
        pygame.draw.line(self.janela.screen, GRAY, (100, current_y), (WINDOW_WIDTH - 100, current_y), 2)
        current_y += 40

        # --- Seção de Power-Ups ---
        header_powerups_surf = self.font_header.render("Power-Ups", True, RED)
        header_powerups_rect = header_powerups_surf.get_rect(center=(WINDOW_WIDTH / 2, current_y))
        self.janela.screen.blit(header_powerups_surf, header_powerups_rect)
        current_y += 50

        self.shield_powerup_sprite.set_position(label_x, current_y)
        self.shield_powerup_sprite.draw()
        self.janela.draw_text("Escudo:", label_x + 50, current_y + 4, font_name=FONT_PATH, size=24, color=GRAY)
        self.janela.draw_text("Protege contra um único dano.", value_x, current_y + 4, font_name=FONT_PATH, size=24, color=WHITE)
        current_y += line_height

        self.fastshot_powerup_sprite.set_position(label_x, current_y)
        self.fastshot_powerup_sprite.draw()
        self.janela.draw_text("Tiro Rápido:", label_x + 50, current_y + 4, font_name=FONT_PATH, size=24, color=GRAY)
        self.janela.draw_text("Aumenta a cadência de tiro.", value_x, current_y + 4, font_name=FONT_PATH, size=24, color=WHITE)
        
        self.back_button.draw(self.janela, self.mouse)
        if self.back_button.is_clicked(is_new_click) or self.teclado.key_pressed("ESC"):
            return GAME_STATE_MENU
            
        return GAME_STATE_HOW_TO_PLAY

class Ranking:
    """Cena que exibe as maiores pontuações."""
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
        """Carrega as pontuações do arquivo de ranking."""
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
            self.janela.draw_text("Nenhuma pontuação registrada.", 220, 280, size=30, color=WHITE, font_name=FONT_PATH)
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
    """Cena de Fim de Jogo para o jogador inserir o nome."""
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
        """Salva a pontuação no arquivo de ranking."""
        if not self.player_name: return
        difficulty_name = DIFFICULTY_SETTINGS[self.difficulty_level]["name"]
        new_entry = f"{self.player_name.replace(' ', '_')} {difficulty_name} {int(self.final_score)}\n"
        
        try:
            with open(RANKING_FILE, 'a') as f: f.write(new_entry)
        except IOError:
            print(f"Erro: Não foi possível escrever no arquivo {RANKING_FILE}")

    def run(self):
        # Lógica de input para o nome do jogador
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

        # Lógica do cursor piscando
        self.cursor_timer += self.janela.delta_time()
        if self.cursor_timer > 0.4:
            self.show_cursor = not self.show_cursor
            self.cursor_timer = 0
            
        # Desenho dos elementos da tela
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