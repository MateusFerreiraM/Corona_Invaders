from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.mouse import Mouse
from menu import Menu
import globais

class Dificuldade(object):
    def __init__(self, janela):
        self.janela = janela
        self.mouse = Mouse()
        self.teclado = Window.get_keyboard()
        self.menu = Menu(janela)

    def run(self):
        self.tela = GameImage("assets/dificuldade.png")
        self.tela.draw()

        #Selecionar dificuldade FÁCIL
        if Mouse.is_over_area(self=self.mouse,start_point=(241,180),end_point=(470,230)):
            if(self.mouse.is_button_pressed(1)):
                globais.DIFICULDADE = 1

        #Selecionar dificuldade MÉDIO
        if Mouse.is_over_area(self=self.mouse,start_point=(241,265),end_point=(470,315)):
            if(self.mouse.is_button_pressed(1)):
                globais.DIFICULDADE = 2

        #Selecionar dificuldade DIFÍCIL
        if Mouse.is_over_area(self=self.mouse,start_point=(335,350),end_point=(470,410)):
            if(self.mouse.is_button_pressed(1)):
                globais.DIFICULDADE = 3

        #Retornar para o MENU
        if Mouse.is_over_area(self=self.mouse,start_point=(335,470),end_point=(565,527)):
            if(self.mouse.is_button_pressed(1)):
                globais.GAME_STATE = 1
        if (self.teclado.key_pressed("ESC")):
            globais.GAME_STATE = 1
