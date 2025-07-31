# =========================================================================================
# --- Constantes de Configuração Geral ---
# =========================================================================================
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
GAME_TITLE = "Corona Invaders"
ASSET_PATH = "assets/"
IMAGES_PATH = "images/"
SOUNDS_PATH = "sounds/"
RANKING_FILE = 'ranking.txt'
GAME_VOLUME = 0.03

# =========================================================================================
# --- Cores e Fonte ---
# =========================================================================================
BACKGROUND_COLOR = (2, 4, 28) 
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 130, 130)
FONT_PATH = ASSET_PATH + "font/VCR_OSD_MONO.ttf" 

# =========================================================================================
# --- Estados do Jogo (State Machine) ---
# =========================================================================================
GAME_STATE_MENU = 1
GAME_STATE_PLAYING = 2
GAME_STATE_DIFFICULTY = 3
GAME_STATE_RANKING = 4
GAME_STATE_GAME_OVER = 5
GAME_STATE_EXIT = 6
GAME_STATE_RESTART = 7
GAME_STATE_HOW_TO_PLAY = 8

# =========================================================================================
# --- Dificuldades ---
# =========================================================================================
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {
        "name": "Fácil", "player_lives": 6, "enemy_base_rows": 2, "enemy_base_cols": 6,
        "enemy_move_speed_mult": 0.8, "enemy_bullet_speed_mult": 0.85,
        "cols_increase_per_level": 0, "levels_per_row_increase": 4,
        "enemy_shot_cooldown_factor": 1.2, "simultaneous_shots": 1,
        "powerup_drop_chance": 0.15, "score_multiplier": 1.0,
    },
    DIFFICULTY_MEDIUM: {
        "name": "Médio", "player_lives": 5, "enemy_base_rows": 3, "enemy_base_cols": 6,
        "enemy_move_speed_mult": 1.0, "enemy_bullet_speed_mult": 1.0,
        "cols_increase_per_level": 1, "levels_per_row_increase": 0,
        "enemy_shot_cooldown_factor": 1.0, "simultaneous_shots": 1,
        "powerup_drop_chance": 0.10, "score_multiplier": 1.5,
    },
    DIFFICULTY_HARD: {
        "name": "Difícil", "player_lives": 3, "enemy_base_rows": 3, "enemy_base_cols": 8,
        "enemy_move_speed_mult": 1.25, "enemy_bullet_speed_mult": 1.5,
        "cols_increase_per_level": 1, "levels_per_row_increase": 2,
        "enemy_shot_cooldown_factor": 0.7, "simultaneous_shots": 2,
        "powerup_drop_chance": 0.05, "score_multiplier": 2.0,
    }
}

# =========================================================================================
# --- Caminhos dos Assets de Imagens e Sons ---
# =========================================================================================
MUSIC_BACKGROUND_PATH = ASSET_PATH + SOUNDS_PATH + "game_music.ogg"
SOUND_PLAYER_SHOOT_PATH = ASSET_PATH + SOUNDS_PATH + "player_shoot.ogg"
SOUND_ENEMY_EXPLOSION_PATH = ASSET_PATH + SOUNDS_PATH + "enemy_explosion.ogg"
SOUND_PLAYER_HIT_PATH = ASSET_PATH + SOUNDS_PATH + "player_hit.ogg"
PLAYER_SPRITE_PATH = ASSET_PATH + IMAGES_PATH + "nave.png"
PLAYER_SHIELD_SPRITE_PATH = ASSET_PATH + IMAGES_PATH + "player_shield.png"
PLAYER_DEATH_ANIM_PATH = ASSET_PATH + IMAGES_PATH + "jogo_jogador-respawn.png"
ENEMY_SPRITE_PATH = ASSET_PATH + IMAGES_PATH + "corona.png"
BOSS_SPRITE_PATH = ASSET_PATH + IMAGES_PATH + "boss.png"
PLAYER_BULLET_PATH = ASSET_PATH + IMAGES_PATH + "gota.png"
POWERUP_BULLET_PATH = ASSET_PATH + IMAGES_PATH + "powerup_gota.png"
ENEMY_BULLET_PATH = ASSET_PATH + IMAGES_PATH + "tirocorona.png"
POWERUP_SHIELD_PATH = ASSET_PATH + IMAGES_PATH + "powerup_shield.png"
POWERUP_FAST_SHOT_PATH = ASSET_PATH + IMAGES_PATH + "powerup_gota.png"

# =========================================================================================
# --- Constantes de Gameplay ---
# =========================================================================================
PLAYER_SPEED = 600
PLAYER_SHOOT_COOLDOWN = 0.5
ENEMY_MOVEMENT_BASE_SPEED = 120
ENEMY_ADVANCE_Y_OFFSET = 15
ENEMY_SHOT_COOLDOWN_BASE = 3
BULLET_SPEED_PLAYER = -420
ENEMY_BULLET_SPEED_BASE = 120
POWERUP_SPEED = 100
POWERUP_SHIELD_DURATION = 5.0
POWERUP_FAST_SHOT_DURATION = 5.0
SCORE_HIT_ENEMY_BASE = 25
SCORE_HIT_BOSS_BASE = 50
SCORE_PASS_LEVEL_BASE = 1000
SCORE_BOSS_DEFEAT_BASE = 5000
ENEMY_SPACING = 15
POWERUP_TYPE_SHIELD = 0
POWERUP_TYPE_FAST_SHOT = 1