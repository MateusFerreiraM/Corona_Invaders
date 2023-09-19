from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.collision import *
import globais
import random

class Jogador(object):
    def __init__(self, janela):
        self.janela = janela
        self.player = Sprite("assets/nave.png")
        self.listaTiros = []
        self.teclado = self.janela.get_keyboard()
        self.cronometroTiros = 0
        self.vidas = 6 - globais.DIFICULDADE
        self.set_pos()

    def set_pos(self):
        self.player.set_position((self.janela.width/2) - (self.player.width/2), self.janela.height - (self.player.height + 5))
    
    def _draw(self):
        self.player.draw()
        for i in range(len(self.listaTiros)):
            self.listaTiros[i].draw()

    def atirar(self):
        tiro = Sprite("assets/gota.png")
        tiro.set_position(self.player.x + self.player.width/2 - tiro.width/2, self.player.y)
        self.listaTiros.append(tiro)

    def atualizarTiros(self):
        for i in range(len(self.listaTiros)):
            self.listaTiros[i].move_y(self.janela.delta_time() * globais.FRAME_PER_SECOND *-7)
            if(self.listaTiros[i].y <= 0):
                self.listaTiros.pop(i)
                break

    def run(self):        
        #Andar para os lados
        self.player.move_key_x(10 * self.janela.delta_time() * globais.FRAME_PER_SECOND)
        
        #Atirar
        if(self.cronometroTiros >= 0.5):
            if(self.teclado.key_pressed("SPACE")):
                self.atirar()
                self.cronometroTiros = 0
        self.cronometroTiros += self.janela.delta_time()

        #Checagem de laterais da tela
        if(self.player.x < 0):
            self.player.set_position(0, self.janela.height-50)

        if(self.player.x + self.player.width > self.janela.width):
            self.player.x = self.janela.width - self.player.width
        
        #Mover os tiros e remover da lista
        self.atualizarTiros()
        self._draw()

class Inimigos(object):
    def __init__(self, janela, nivel):
        self.janela = janela
        self.nivel = nivel
        self.matrizInimigos = []
        self.quantidadeColunas = globais.DIFICULDADE + 1 
        self.quantidadeLinhas = globais.DIFICULDADE
        self.quantidadeInimigos = self.quantidadeColunas * self.quantidadeLinhas
        self.velocidadeInimigos = (3 * globais.DIFICULDADE * self.janela.delta_time() * self.nivel)/self.quantidadeInimigos
        self.direcaoInimigos = 1
        self.listaTiros = []
        self.cronometroTiro = 0
        self.cronometroAvancar = 0
        self.velocidadeTiro = 2 + (70 / self.quantidadeInimigos) * 0.2 + self.nivel * 0.5
        self.spawn()

    def spawn(self):
        for i in range(self.quantidadeLinhas):
            self.matrizInimigos.append([])
            for j in range(self.quantidadeColunas):
                self.matrizInimigos[i].append(Sprite("assets/corona.png"))
                self.matrizInimigos[i][j].set_position((j+1)* (self.janela.width/(self.janela.width/60)), (i+1)*50)
        
    def moverInimigos(self):
        #Atualizando velocidade dos inimigos
        if self.quantidadeInimigos > 0:
            self.velocidadeInimigos =  (self.janela.delta_time() * globais.FRAME_PER_SECOND) * self.direcaoInimigos + self.direcaoInimigos * globais.DIFICULDADE/3 + self.direcaoInimigos * 2 / self.quantidadeInimigos
        
        for i in range(len(self.matrizInimigos)):
            for j in range(len(self.matrizInimigos[i])):
                self.matrizInimigos[i][j].move_x(self.velocidadeInimigos)
    
    def atirar(self):
        if self.cronometroTiro > 4 / globais.DIFICULDADE + (self.nivel * 0.5):
            selecionado = random.randint(0, self.quantidadeInimigos)
            aux = 0
           
            for i in range(len(self.matrizInimigos)):
                for j in range(len(self.matrizInimigos[i])):
                    aux += 1
                    if aux == selecionado:
                        tiro = Sprite("assets/tirocorona.png")
                        tiro.set_position(self.matrizInimigos[i][j].x + self.matrizInimigos[i][j].width/2 - tiro.width/2, self.matrizInimigos[i][j].y)
                        self.listaTiros.append(tiro)
                        self.cronometroTiro = 0
                        return
        else: self.cronometroTiro += self.janela.delta_time()

    def atualizarTiros(self):
        self.velocidadeTiro = 2 + (70 / self.quantidadeInimigos) * 0.2 + self.nivel * 0.5
        
        for i in range(len(self.listaTiros)):
            self.listaTiros[i].move_y(self.janela.delta_time() * globais.FRAME_PER_SECOND * self.velocidadeTiro)
            if(self.listaTiros[i].y <= 0):
                self.listaTiros.pop(i)
                break

    def checarLimitesLaterais(self):
        for i in range(len(self.matrizInimigos)):
            for j in range(len(self.matrizInimigos[i])):
                if (self.matrizInimigos[i][j].x <= 0) or (self.matrizInimigos[i][j].x >= (self.janela.width - self.matrizInimigos[i][j].width)):
                    return True
        return False

    def avancarInimigos(self):
        if self.cronometroAvancar > 0.15:
            if self.checarLimitesLaterais():
                self.direcaoInimigos = -self.direcaoInimigos
                for i in range(len(self.matrizInimigos)):
                    for j in range(len(self.matrizInimigos[i])):
                        self.matrizInimigos[i][j].y += 20
                self.cronometroAvancar = 0
        else: self.cronometroAvancar += self.janela.delta_time()

    def _draw(self):
        for i in range(len(self.matrizInimigos)):
            for j in range(len(self.matrizInimigos[i])):
                self.matrizInimigos[i][j].draw()
                
        for i in range(len(self.listaTiros)):
            self.listaTiros[i].draw()
    
    def run(self):
        self.moverInimigos()
        self.avancarInimigos()
        self.atirar()
        self.atualizarTiros()
        self._draw()