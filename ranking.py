from dificuldade import Dificuldade
from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.mouse import Mouse
import globais

class Ranking(object):
    def __init__(self, janela):
        self.janela = janela
        self.teclado = janela.get_keyboard()
        self.titulo = Sprite("assets/ranking_titulo.png", 1)
        self.set_pos()
        self._draw()

    def set_pos(self):
        self.titulo.set_position(self.janela.width/2 - self.titulo.width/2, 25)

    def _draw(self):
        self.titulo.draw()

    def run(self):
        self._draw()
        arq = open('ranking.txt','r')
        conteudo = arq.readlines()
        nomes=[]
        dificuldades=[]
        pontos=[]
        for i in range(len(conteudo)):
            linha=conteudo[i].split()
            nomes.append(linha[0])
            dificuldades.append(linha[1])
            pontos.append(int(linha[2].rstrip('\n')))
        arq.close()
        for j in range(5):
            for i in range(len(pontos)-1):
                if pontos[i]<pontos[i+1]:
                    pontos[i+1],pontos[i]=pontos[i],pontos[i+1]
                    nomes[i+1],nomes[i]=nomes[i],nomes[i+1]

        for i in range(len(nomes)):
            if i>4:
                break
            self.janela.draw_text("{}º {} - Pontos: {} - Dificuldade: {}".format(i+1, nomes[i], pontos[i], dificuldades[i]), 200, 100+i*50, size=32, color=(255, 255, 255), font_name="Arial")
        
        if(self.teclado.key_pressed("ESC")):
            globais.GAME_STATE =  1