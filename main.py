from PPlay.keyboard import Keyboard
from PPlay.window import Window
from PPlay.mouse import *
from menu import Menu
from dificuldade import Dificuldade
from ranking import Ranking
from jogo import Jogar
import globais

janela = Window(globais.WIDTH, globais.HEIGHT)
janela.set_title("Corona Invaders")
teclado = Window.get_keyboard()
mouse = Window.get_mouse()
menu = Menu(janela)
dificuldade = Dificuldade(janela)
ranking = Ranking(janela)
jogo = Jogar(janela)

while globais.GAME_STATE != 5:
    janela.set_background_color((0,0,0))

    if globais.GAME_STATE == 1:
        menu.run()

    elif globais.GAME_STATE == 2:
        jogo.run()

    elif globais.GAME_STATE == 3:
        dificuldade.run()
        jogo = Jogar(janela)
        
    elif globais.GAME_STATE == 4:
        ranking.run()

    janela.update()