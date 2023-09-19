from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.mouse import *
import globais

class Menu(object):
    def __init__(self, janela):
        self.janela = janela
        self.tela = GameImage("assets/menu.png")
        self.teclado = Window.get_keyboard()
        self.mouse = Window.get_mouse()

    def run(self):
        self.tela.draw()
        #Iniciar o jogo
        if Mouse.is_over_area(self=self.mouse,start_point=(335,180),end_point=(567,230)):
            if(self.mouse.is_button_pressed(1)):
                globais.GAME_STATE = 2

        #Ir para o menu de dificuldade
        if Mouse.is_over_area(self=self.mouse,start_point=(335,265),end_point=(567,315)):
            if(self.mouse.is_button_pressed(1)):
                globais.GAME_STATE = 3

        #Ver o Ranking
        if Mouse.is_over_area(self=self.mouse,start_point=(335,350),end_point=(567,400)):
            if(self.mouse.is_button_pressed(1)):
                globais.GAME_STATE = 4

        #Fechar o jogo
        if Mouse.is_over_area(self=self.mouse,start_point=(335,435),end_point=(567,485)):
            if(self.mouse.is_button_pressed(1)):
                globais.GAME_STATE = 5
