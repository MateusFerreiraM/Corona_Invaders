from PPlay.sound import *
from constants import *

class AssetManager:
    """Carrega e gerencia todos os assets de áudio do jogo para fácil acesso."""
    def __init__(self):
        """Carrega todos os arquivos de som na memória ao ser instanciada."""
        self.player_shoot = Sound(SOUND_PLAYER_SHOOT_PATH)
        self.player_hit = Sound(SOUND_PLAYER_HIT_PATH)
        self.enemy_explosion = Sound(SOUND_ENEMY_EXPLOSION_PATH)
        self.background_music = Sound(MUSIC_BACKGROUND_PATH)
        
    def set_volume(self, volume):
        """Define um volume global (0 a 1.0) para todos os sons."""
        vol_int = int(volume * 100)
        self.player_shoot.set_volume(vol_int)
        self.player_hit.set_volume(vol_int)
        self.enemy_explosion.set_volume(vol_int)
        self.background_music.set_volume(vol_int)