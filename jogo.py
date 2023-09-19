from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.gameobject import *
from PPlay.collision import *
from PPlay.animation import *
from atores import Jogador, Inimigos
import globais

class Jogar(object):
    def __init__(self, janela):
        self.janela = janela
        self.pontuacao = 0
        self.tempo = 0
        self.nivel = 1
        self.FPS = 0
        self.fpsAtual = 0
        self.cronometroFPS = 0
        self.teclado = janela.get_keyboard()
        self.jogador = Jogador(self.janela)
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.vivo = True
        self.playerDead = Animation("assets/jogo_jogador-respawn.png", 12)
        self.playerDead.set_total_duration(1000)
        self.cronometroMorte = 1

    def TiroNoInimigo(self):
        for i in range(len(self.inimigos.matrizInimigos)):
            for j in range(len(self.inimigos.matrizInimigos[i])):
                for k in range(len(self.jogador.listaTiros)):
                    if(Collision.collided(self.jogador.listaTiros[k], self.inimigos.matrizInimigos[i][j])):
                        self.pontuacao += 50 + 50 / self.tempo
                        self.inimigos.matrizInimigos[i].pop(j)
                        self.jogador.listaTiros.pop(k)
                        if(len(self.inimigos.matrizInimigos[i])) == 0:
                            self.inimigos.matrizInimigos.pop(i)
                        self.inimigos.quantidadeInimigos -= 1
                        return

    def reset(self):
        self.nivel = 1
        self.pontuacao = 0
        self.vivo = True
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.jogador = Jogador(self.janela)
        self.cronometroMorte = 1

    def PassarDeNivel(self):
        self.pontuacao += self.nivel * 1000
        self.nivel += 1
        self.inimigos.quantidadeColunas += 1
        self.inimigos.quantidadeLinhas += 1
        self.inimigos.direcaoInimigos = self.inimigos.direcaoInimigos * 1.2 #Ao passar de nível, a velocidade dos monstros aumentas
        self.jogador.listaTiros.clear()
        self.inimigos.listaTiros.clear()
        self.tempo = 0
        self.inimigos.spawn()
        self.inimigos.quantidadeInimigos = self.inimigos.quantidadeColunas * self.inimigos.quantidadeLinhas

    def checarGameOverY(self):
        for i in range(len(self.inimigos.matrizInimigos)):
            for j in range(len(self.inimigos.matrizInimigos[i])):
                if (self.inimigos.matrizInimigos[i][j].y + self.inimigos.matrizInimigos[i][j].height >= self.jogador.player.y):
                    return True
        return False

    def TiroNoPlayer(self):
        for i in range(len(self.inimigos.listaTiros)):
            if Collision.collided(self.inimigos.listaTiros[i], self.jogador.player):
                self.jogador.vidas -= 1
                self.inimigos.listaTiros.pop(i)
                self.cronometroMorte = 0
                self.playerDead.set_curr_frame(0)
                self.playerDead.set_position((self.janela.width/2) - (self.jogador.player.width/2), self.janela.height - (self.jogador.player.height + 5))
                if self.jogador.vidas != 0:
                    self.respawn()
                break

    def respawn(self):            
        self.jogador.player.set_position((self.janela.width/2) - (self.jogador.player.width/2), self.janela.height - (self.jogador.player.height + 5))

    def gameOver(self):            
        arq = open('ranking.txt','r')
        conteudo = arq.readlines()
        nome=str(input('Digite seu nome: '))
        if globais.DIFICULDADE == 1:
            self.nivelfinal = "fácil"
        if globais.DIFICULDADE == 2:
            self.nivelfinal = "médio"
        if globais.DIFICULDADE == 3:
            self.nivelfinal = "difícil"
        linha = nome + ' ' + self.nivelfinal + ' ' + str(int(self.pontuacao)) + '\n'
        conteudo.append(linha)
        arq.close()
        arq = open('ranking.txt', 'w')
        arq.writelines(conteudo)
        arq.close()
        print('Ranking atualizado com sucesso')
        self.inimigos = Inimigos(self.janela, self.nivel)
        self.jogador = Jogador(self.janela)
        self.reset()
        globais.GAME_STATE = 1

    def run(self):
        self.cronometroFPS += self.janela.delta_time()
        self.FPS += 1
        if self.cronometroFPS > 1: 
            self.fpsAtual = self.FPS   
            self.FPS = 0
            self.cronometroFPS = 0
            
        if self.vivo: 
            if self.inimigos.quantidadeInimigos == 0:
                self.PassarDeNivel()
            self.inimigos.run()
            self.jogador.run()
            self.TiroNoInimigo()
            self.TiroNoPlayer()

            self.tempo += self.janela.delta_time()
            
            if(self.teclado.key_pressed("ESC")):
                globais.GAME_STATE = 1
                self.reset()

            if self.checarGameOverY() or self.jogador.vidas == 0:
                self.nivel = 1
                self.vivo = False

            #Desenhando textos
            self.janela.draw_text("Vidas: " + str(self.jogador.vidas), 300, 5, size=28, color=(255,255,255), font_name="Arial")
            self.janela.draw_text("FPS:"+str(self.fpsAtual), 0, 0, size=25, color=(255,255,255))
            self.janela.draw_text("Nivel: " + str(self.nivel), 400, 5, size=28, color=(255,255,255), font_name="Arial")
            self.janela.draw_text("Pontos: " + str(int(self.pontuacao)), 500, 5, size=28, color=(255,255,255), font_name="Arial")
        else:
            self.gameOver()

        #Animação quando morre
        if self.cronometroMorte < 0.9:
                self.playerDead.draw()
                self.playerDead.update()
                self.cronometroMorte += self.janela.delta_time()
