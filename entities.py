import random
from PPlay.sprite import *
from PPlay.animation import *
from constants import *

class Jogador:
    """Gerencia o estado e as ações do jogador."""
    def __init__(self, janela, assets, settings):
        self.janela = janela
        self.assets = assets
        self.player = Sprite(PLAYER_SPRITE_PATH)
        self.shield_sprite = Sprite(PLAYER_SHIELD_SPRITE_PATH)
        self.listaTiros = []
        self.teclado = self.janela.get_keyboard()
        self.cronometroTiros = 0
        self.vidas = settings["player_lives"]
        self.has_shield = False
        self.shield_timer = 0.0
        self.is_fast_shooting = False
        self.fast_shot_timer = 0.0
        self.set_initial_pos()

    def set_initial_pos(self):
        self.player.set_position((self.janela.width / 2) - (self.player.width / 2), self.janela.height - self.player.height - 5)

    def atirar(self):
        caminho_tiro = POWERUP_BULLET_PATH if self.is_fast_shooting else PLAYER_BULLET_PATH
        tiro = Sprite(caminho_tiro)
        tiro.set_position(self.player.x + self.player.width / 2 - tiro.width / 2, self.player.y)
        self.listaTiros.append(tiro)
        self.assets.player_shoot.play()

    def run(self, offset_x=0, offset_y=0):
        dt = self.janela.delta_time()
        if self.teclado.key_pressed("LEFT"): self.player.x -= PLAYER_SPEED * dt
        if self.teclado.key_pressed("RIGHT"): self.player.x += PLAYER_SPEED * dt
        self.player.x = max(0, min(self.player.x, self.janela.width - self.player.width))

        self.cronometroTiros += dt
        cooldown = PLAYER_SHOOT_COOLDOWN * (0.5 if self.is_fast_shooting else 1)
        if self.teclado.key_pressed("SPACE") and self.cronometroTiros >= cooldown:
            self.atirar(); self.cronometroTiros = 0

        if self.has_shield:
            self.shield_timer -= dt
            if self.shield_timer <= 0: self.has_shield = False
        if self.is_fast_shooting:
            self.fast_shot_timer -= dt
            if self.fast_shot_timer <= 0: self.is_fast_shooting = False

        self.listaTiros = [tiro for tiro in self.listaTiros if tiro.y > -tiro.height]
        for tiro in self.listaTiros:
            tiro.move_y(BULLET_SPEED_PLAYER * dt)
            tiro.x += offset_x
            tiro.y += offset_y
            tiro.draw()
            tiro.x -= offset_x
            tiro.y -= offset_y
            
        self.player.x += offset_x
        self.player.y += offset_y
        self.player.draw()
        self.player.x -= offset_x
        self.player.y -= offset_y

        if self.has_shield:
            self.shield_sprite.set_position(self.player.x + (self.player.width - self.shield_sprite.width) / 2, self.player.y + (self.player.height - self.shield_sprite.height) / 2)
            self.shield_sprite.x += offset_x
            self.shield_sprite.y += offset_y
            self.shield_sprite.draw()
            self.shield_sprite.x -= offset_x
            self.shield_sprite.y -= offset_y

class Inimigos:
    """Gerencia a criação, movimento e ações dos inimigos."""
    def __init__(self, janela, nivel, settings):
        self.janela = janela
        self.nivel = nivel
        self.settings = settings
        self.matrizInimigos = []
        self.listaTiros = []
        self.direcao = 1
        self.cronometroTiro = 0
        self.spawn()

    def spawn(self):
        self.matrizInimigos = []
        
        cols_adicionais = (self.nivel - 1) * self.settings["cols_increase_per_level"]
        levels_per_row = self.settings["levels_per_row_increase"]
        rows_adicionais = (self.nivel - 1) // levels_per_row if levels_per_row > 0 else 0

        cols = self.settings["enemy_base_cols"] + cols_adicionais
        rows = self.settings["enemy_base_rows"] + rows_adicionais
        
        max_cols = (self.janela.width // (Sprite(ENEMY_SPRITE_PATH).width + ENEMY_SPACING)) - 1
        cols = min(cols, max_cols)

        temp_enemy = Sprite(ENEMY_SPRITE_PATH)
        enemy_w = temp_enemy.width + ENEMY_SPACING
        enemy_h = temp_enemy.height + ENEMY_SPACING

        grid_width = cols * enemy_w
        start_x = (self.janela.width - grid_width) / 2
        
        for i in range(rows):
            linha = []
            for j in range(cols):
                inimigo = Sprite(ENEMY_SPRITE_PATH)
                inimigo.set_position(start_x + j * enemy_w, 70 + i * enemy_h)
                linha.append(inimigo)
            self.matrizInimigos.append(linha)
    
    @property
    def quantidade_total(self):
        return sum(len(linha) for linha in self.matrizInimigos)

    def run(self, offset_x=0, offset_y=0):
        dt = self.janela.delta_time()
        qtd_inimigos = self.quantidade_total
        if qtd_inimigos == 0: return

        move_speed = (ENEMY_MOVEMENT_BASE_SPEED * 0.6) * self.settings["enemy_move_speed_mult"]
        speed_multiplier = (move_speed + self.nivel * 10 + 200 / qtd_inimigos)
        vx = self.direcao * speed_multiplier * dt
        
        chegou_na_borda = False
        for linha in self.matrizInimigos:
            for inimigo in linha:
                inimigo.move_x(vx)
                if not chegou_na_borda and (inimigo.x < 0 or (inimigo.x + inimigo.width) > self.janela.width):
                    chegou_na_borda = True
        
        if chegou_na_borda:
            self.direcao *= -1
            descida_y = ENEMY_ADVANCE_Y_OFFSET + self.nivel
            
            overshoot = 0
            if self.direcao == 1:
                min_x = min(i.x for l in self.matrizInimigos for i in l)
                overshoot = 0 - min_x
            else:
                max_x = max(i.x + i.width for l in self.matrizInimigos for i in l)
                overshoot = max_x - self.janela.width
            
            for linha in self.matrizInimigos:
                for inimigo in linha:
                    inimigo.y += descida_y
                    inimigo.x += self.direcao * overshoot

        self.cronometroTiro += dt
        cooldown = (ENEMY_SHOT_COOLDOWN_BASE - self.nivel * 0.1) * self.settings["enemy_shot_cooldown_factor"]
        if self.cronometroTiro > max(0.3, cooldown):
            self.cronometroTiro = 0
            atiradores_disponiveis = [inimigo for linha in self.matrizInimigos for inimigo in linha]
            if atiradores_disponiveis:
                num_tiros = min(self.settings["simultaneous_shots"], len(atiradores_disponiveis))
                atiradores_selecionados = random.sample(atiradores_disponiveis, num_tiros)
                
                for atirador in atiradores_selecionados:
                    tiro = Sprite(ENEMY_BULLET_PATH)
                    tiro.set_position(atirador.x + atirador.width/2 - tiro.width/2, atirador.y + atirador.height)
                    self.listaTiros.append(tiro)

        base_speed = ENEMY_BULLET_SPEED_BASE + (self.nivel * 10)
        v_tiro = base_speed * self.settings["enemy_bullet_speed_mult"]
        self.listaTiros = [tiro for tiro in self.listaTiros if tiro.y < self.janela.height]
        for tiro in self.listaTiros:
            tiro.move_y(v_tiro * dt)
            tiro.x += offset_x
            tiro.y += offset_y
            tiro.draw()
            tiro.x -= offset_x
            tiro.y -= offset_y

        for linha in self.matrizInimigos:
            for inimigo in linha:
                inimigo.x += offset_x
                inimigo.y += offset_y
                inimigo.draw()
                inimigo.x -= offset_x
                inimigo.y -= offset_y

class PowerUp(Sprite):
    """Representa um item de power-up que cai na tela."""
    def __init__(self, x, y, type_id):
        path = POWERUP_SHIELD_PATH if type_id == POWERUP_TYPE_SHIELD else POWERUP_FAST_SHOT_PATH
        super().__init__(path)
        self.set_position(x, y)
        self.type_id = type_id

    def run(self, dt, offset_x=0, offset_y=0):
        self.move_y(POWERUP_SPEED * dt)
        self.x += offset_x
        self.y += offset_y
        self.draw()
        self.x -= offset_x
        self.y -= offset_y

class Boss:
    """Gerencia o chefão (inimigo gigante)."""
    def __init__(self, janela, nivel, settings):
        self.janela = janela
        self.nivel = nivel
        self.settings = settings
        self.sprite = Sprite(BOSS_SPRITE_PATH) 
        self.sprite.set_position(janela.width / 2 - self.sprite.width / 2, 80)
        
        self.max_health = 20 + (nivel * 4)
        self.health = self.max_health
        self.listaTiros = []
        self.direcao = 1
        self.move_speed = (ENEMY_MOVEMENT_BASE_SPEED * 0.6) * self.settings["enemy_move_speed_mult"]
        self.shot_cooldown = max(0.8, 2.5 - (nivel * 0.1)) * self.settings["enemy_shot_cooldown_factor"]

        self.shot_timer = 0
        self.pattern_timer = 0
        self.pattern_duration = 7.0
        self.current_pattern = 0

    def _shoot_barrage(self):
        """Atira uma rajada de 3 tiros rápidos em sequência."""
        for i in range(3):
            tiro = Sprite(ENEMY_BULLET_PATH)
            offset_x = self.sprite.x + self.sprite.width/2 - tiro.width/2
            offset_y = self.sprite.y + self.sprite.height + (i * 30)
            tiro.set_position(offset_x, offset_y)
            self.listaTiros.append(tiro)

    def _shoot_spread(self):
        """Atira 3 projéteis de uma vez em posições diferentes."""
        for i in range(-1, 2):
            tiro = Sprite(ENEMY_BULLET_PATH)
            offset_x = self.sprite.x + self.sprite.width/2 - tiro.width/2 + (i * 60)
            offset_y = self.sprite.y + self.sprite.height
            tiro.set_position(offset_x, offset_y)
            self.listaTiros.append(tiro)

    def run(self, dt, offset_x=0, offset_y=0):
        self.sprite.move_x(self.direcao * self.move_speed * dt)
        if self.sprite.x < 0 or (self.sprite.x + self.sprite.width) > self.janela.width:
            self.direcao *= -1
            self.sprite.x += self.direcao * 5

        self.pattern_timer += dt
        if self.pattern_timer >= self.pattern_duration:
            self.pattern_timer = 0
            self.current_pattern = (self.current_pattern + 1) % 2

        self.shot_timer += dt
        if self.shot_timer >= self.shot_cooldown:
            self.shot_timer = 0
            if self.current_pattern == 0: self._shoot_barrage()
            else: self._shoot_spread()

        v_tiro = (ENEMY_BULLET_SPEED_BASE + (self.nivel * 8)) * self.settings["enemy_bullet_speed_mult"]
        self.listaTiros = [tiro for tiro in self.listaTiros if tiro.y < self.janela.height]
        for tiro in self.listaTiros:
            tiro.move_y(v_tiro * dt)
            tiro.x += offset_x
            tiro.y += offset_y
            tiro.draw()
            tiro.x -= offset_x
            tiro.y -= offset_y

        self.sprite.x += offset_x
        self.sprite.y += offset_y
        self.sprite.draw()
        self.sprite.x -= offset_x
        self.sprite.y -= offset_y