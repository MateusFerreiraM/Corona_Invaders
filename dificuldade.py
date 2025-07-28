from PPlay.window import Window
from PPlay.sprite import Sprite
from PPlay.gameimage import GameImage
from PPlay.mouse import Mouse
import globais

# Sugestão: Adicionar estas constantes em globais.py
# Ou mantê-las aqui se forem muito específicas desta tela
class DificuldadeConstantes:
    EASY_BUTTON_COORDS = (241, 180, 470, 230)
    MEDIUM_BUTTON_COORDS = (241, 265, 470, 315)
    HARD_BUTTON_COORDS = (335, 350, 470, 410) # Notei uma mudança no X e no tamanho para o difícil, talvez seja intencional ou um erro de digitação.
    BACK_BUTTON_COORDS = (335, 470, 565, 527)

    DIFICULDADE_FACIL = 1
    DIFICULDADE_MEDIO = 2
    DIFICULDADE_DIFICIL = 3


class Dificuldade(object):
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.teclado = self.janela.get_keyboard() # Acessar o teclado da instância da janela

        # Carregar a imagem de fundo apenas uma vez
        self.tela = GameImage("assets/dificuldade.png")

        # Criar "sprites" para os botões (mesmo que invisíveis, apenas para a área de clique)
        # Se você tiver imagens para os botões, substitua GameImage por Sprite e desenhe-os.
        # Aqui, estamos usando retângulos imaginários para as áreas de clique.
        # Poderíamos até criar sprites com uma imagem simples para cada botão se houvesse.
        # Exemplo com Sprite: self.botao_facil = Sprite("assets/botao_facil.png")
        # self.botao_facil.set_position(241, 180)

        # Para manter a simplicidade com as áreas existentes, vou usar tuplas para as áreas.
        # O ideal seria ter sprites ou uma classe Botao dedicada.

    def _check_button_click(self, coords, difficulty_value=None, game_state_change=None):
        """Método auxiliar para verificar cliques em botões."""
        if self.mouse.is_over_area(start_point=(coords[0], coords[1]), end_point=(coords[2], coords[3])):
            if self.mouse.is_button_pressed(1):
                if difficulty_value is not None:
                    globais.DIFICULDADE = difficulty_value
                if game_state_change is not None:
                    globais.GAME_STATE = game_state_change
                return True # Retorna True se o botão foi clicado
        return False

    def run(self):
        self.tela.draw()

        # Selecionar dificuldade FÁCIL
        self._check_button_click(DificuldadeConstantes.EASY_BUTTON_COORDS, difficulty_value=DificuldadeConstantes.DIFICULDADE_FACIL)

        # Selecionar dificuldade MÉDIO
        self._check_button_click(DificuldadeConstantes.MEDIUM_BUTTON_COORDS, difficulty_value=DificuldadeConstantes.DIFICULDADE_MEDIO)

        # Selecionar dificuldade DIFÍCIL
        self._check_button_click(DificuldadeConstantes.HARD_BUTTON_COORDS, difficulty_value=DificuldadeConstantes.DIFICULDADE_DIFICIL)

        # Retornar para o MENU
        self._check_button_click(DificuldadeConstantes.BACK_BUTTON_COORDS, game_state_change=globais.GAME_STATE_MENU) # Assumindo GAME_STATE_MENU = 1
        
        # O PPlay já captura o ESC automaticamente.
        if self.teclado.key_pressed("ESC"):
            globais.GAME_STATE = globais.GAME_STATE_MENU # Assumindo GAME_STATE_MENU = 1