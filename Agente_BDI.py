from desenharMapa import inicializar_ambiente
from agente import aspiradorSimples
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np    
import heapq

class Agente_BDI:
    def __init__(self, tamanho):
        self.beliefs = [] #guarda coordenadas de sujeira
        self.desires = []
        self.intentions = []
        self.plans = []
        self.grid = inicializar_ambiente(tamanho)
        self.bateria = 30


    def pode_mover(self, nx, ny):
        tamanho = len(self.grid)
        if 0 <= nx < tamanho and 0 <= ny < tamanho and self.grid[nx][ny] != "movel":
            return True
        return False
    
    def detecta_tipo_sujeira(sujeira):
        if sujeira == "poeira":
            return 1
        elif sujeira == "liquido":
            return 2
        else:
            return 3
    
    def perceive(self, posicao): #analisa espaços próximos e guarda em beliefs onde tem sujeira e seu tipo
        """
        Analisa espaços próximos e guarda em beliefs onde tem sujeira e seu tipo
        Retorno: self.beliefs recebe posição e tipos das sujeiras detectadas
        """
        sujeira = {"poeira", "liquido", "detritos"}
        tamanho = len(self.grid)
        espaço_sujo = {}
        x = posicao[0]
        y = posicao[1]

        #Detecta Sul
        if x + 1 < tamanho and self.pode_mover(x + 1, y) and self.grid[x + 1][y] in sujeira:
            espaço_sujo = {"coord": (x+1,y), "pontos": self.detecta_tipo_sujeira(sujeira)}
            self.beliefs.append(espaço_sujo)
        #Detecta Norte
        if x - 1 >= 0 and self.pode_mover(x - 1, y) and self.grid[x - 1][y] in sujeira:
            espaço_sujo = {"coord": (x-1,y), "pontos": self.detecta_tipo_sujeira(sujeira)}
            self.beliefs.append(espaço_sujo)
        #Detecta leste
        if y + 1 < tamanho and self.pode_mover(x, y + 1) and self.grid[x][y + 1] in sujeira:
            espaço_sujo = {"coord": (x,y+1), "pontos": self.detecta_tipo_sujeira(sujeira)}
            self.beliefs.append(espaço_sujo)
        #Detecta oeste
        if y - 1 >= 0 and self.pode_mover(x, y - 1) and self.grid[x][y - 1] in sujeira:
            espaço_sujo = {"coord": (x,y-1), "pontos": self.detecta_tipo_sujeira(sujeira)}
            self.beliefs.append(espaço_sujo)

    def distancia_a_estrela(self,inicio,fim):
        if inicio == fim:
            return 0
    
        linhas, colunas = len(self.grid), len(self.grid[0])
        
        def heuristica(pos):
            return abs(pos[0] - fim[0]) + abs(pos[1] - fim[1])
        
        # fila: (f_score, g_score, posicao)
        fila = [(heuristica(inicio), 0, inicio)]
        visitados = {}
        visitados[inicio] = 0
        
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        while fila:
            f_score, g_score, (x, y) = heapq.heappop(fila)
            
            if (x, y) == fim:
                return g_score
            
            # Ignora se já encontrou caminho melhor
            if g_score > visitados.get((x, y), float('inf')):
                continue
            
            for dx, dy in direcoes:
                nx, ny = x + dx, y + dy
                
                if (0 <= nx < linhas and 0 <= ny < colunas and 
                    self.grid[nx][ny] != "movel"):
                    
                    novo_g = g_score + 1
                    
                    if novo_g < visitados.get((nx, ny), float('inf')):
                        visitados[(nx, ny)] = novo_g
                        f = novo_g + heuristica((nx, ny))
                        heapq.heappush(fila, (f, novo_g, (nx, ny)))
        
        return float('inf')    
    
    def calcula_melhor_rota(self, posicao_inicial, grafo):
        """
        Calcula a melhor rota de limpeza usando algoritmo guloso.

        Estratégia:
        - A partir da posição inicial, escolhe a próxima sujeira com melhor score
        - Score = (pontuacao^2) / (distancia+1)
        - Prioriza alta pontuação e baixa distância
        - Usa distâncias do grafo (já calculadas com A*)

        Parâmetros:
        - posicao_inicial: tupla (x, y) da posição inicial do agente
        - grafo: dicionário {posicao: {destino: distancia}}

        Retorna: lista ordenada de beliefs representando a rota ótima
        """
        if not self.beliefs:
            return []

        rota = []
        visitados = set()
        pos_atual = posicao_inicial
        distancia_total = 0
        pontuacao_total = 0

        # Enquanto houver sujeiras não visitadas
        while len(visitados) < len(self.beliefs):
            melhor_score = -float('inf')
            melhor_belief = None
            melhor_distancia = 0

            # Avalia cada sujeira não visitada
            for belief in self.beliefs:
                coord = belief["coord"]

                if coord not in visitados:
                    # Pega distância do grafo (já calculada com A*)
                    if pos_atual in grafo and coord in grafo[pos_atual]:
                        distancia = grafo[pos_atual][coord]
                    else:
                        distancia = float('inf')

                    # Se inacessível, pula esta sujeira
                    if distancia == float('inf'):
                        continue

                    pontuacao = belief["pontos"]

                    # Heurística de score:
                    # - pontuacao^2: dá peso exponencial (detritos=9, líquido=4, poeira=1)
                    # - distancia+1: evita divisão por zero e penaliza distâncias longas
                    score = (pontuacao ** 2) / (distancia+1)

                    if score > melhor_score:
                        melhor_score = score
                        melhor_belief = belief
                        melhor_distancia = distancia

            # Adiciona melhor escolha à rota
            if melhor_belief:
                rota.append(melhor_belief)
                visitados.add(melhor_belief["coord"])
                distancia_total += melhor_distancia
                pontuacao_total += melhor_belief["pontos"]
                pos_atual = melhor_belief["coord"]
            else:
                # Não há mais sujeiras acessíveis
                break

        # Armazena estatísticas da rota calculada
        self.rota_info = {
            'distancia_total': distancia_total,
            'pontuacao_total': pontuacao_total,
            'eficiencia': pontuacao_total / (distancia_total + 1),
            'num_sujeiras_rota': len(rota),
            'num_sujeiras_total': len(self.beliefs)
        }

        return rota

    def update_desires(self, posicao_atual): #calcula melhor rota (maior pontuação) para limpar a sujeira conhecida
        """
        Atualiza desires com a melhor rota de limpeza.

        Processo:
        1. Cria grafo conectando posição atual e todas as sujeiras
        2. Calcula distâncias reais usando A* (considerando obstáculos)
        3. Calcula melhor rota (menor distância + maior pontuação)
        4. Armazena rota em self.desires
        """
        if not self.beliefs:
            self.desires = []
            self.grafo = {}
            return

        grafo = {}  # {posicao: {destino: distancia}}
        nos = [posicao_atual] + [b["coord"] for b in self.beliefs]

        for no in nos:
            grafo[no] = {}
            for outro_no in nos:
                if outro_no != no:
                    # Usa A* para calcular distância real considerando obstáculos
                    distancia = self.distancia_a_estrela(no, outro_no)
                    grafo[no][outro_no] = distancia

        self.desires = self.calcula_melhor_rota(posicao_atual, grafo)
        
    def calcular_proximo_passo(self, posicao_atual, destino):
        """
        Calcula apenas o próximo passo (uma casa) no caminho até o destino.
        Usa A* para encontrar o caminho e retorna apenas a primeira direção.

        Parâmetros:
        - posicao_atual: tupla (x, y) da posição atual
        - destino: tupla (x, y) do destino

        Retorna: direção ('N', 'S', 'L', 'O') ou None se já chegou/inacessível
        """
        if posicao_atual == destino:
            return None

        linhas, colunas = len(self.grid), len(self.grid[0])

        def heuristica(pos):
            return abs(pos[0] - destino[0]) + abs(pos[1] - destino[1])

        # A*: (f_score, g_score, posicao, caminho)
        fila = [(heuristica(posicao_atual), 0, posicao_atual, [])]
        visitados = {}
        visitados[posicao_atual] = 0

        direcoes = {
            (1, 0): 'S',   # Sul
            (-1, 0): 'N',  # Norte
            (0, 1): 'L',   # Leste
            (0, -1): 'O'   # Oeste
        }

        while fila:
            f_score, g_score, (x, y), caminho = heapq.heappop(fila)

            if (x, y) == destino:
                # Retorna apenas a primeira direção do caminho
                return caminho[0] if caminho else None

            if g_score > visitados.get((x, y), float('inf')):
                continue

            for (dx, dy), direcao in direcoes.items():
                nx, ny = x + dx, y + dy

                if (0 <= nx < linhas and 0 <= ny < colunas and
                    self.grid[nx][ny] != "movel"):

                    novo_g = g_score + 1

                    if novo_g < visitados.get((nx, ny), float('inf')):
                        visitados[(nx, ny)] = novo_g
                        f = novo_g + heuristica((nx, ny))
                        novo_caminho = caminho + [direcao]
                        heapq.heappush(fila, (f, novo_g, (nx, ny), novo_caminho))

        return None  # Inacessível

    def update_intentions(self, posicao_atual):
        """
        Atualiza intentions com a próxima ação a ser executada.
        Move apenas UMA casa em direção ao primeiro objetivo em desires.

        Filosofia BDI:
        - Depois de cada ação, o agente reperceive o ambiente
        - Recalcula beliefs e desires se necessário
        - Permite reatividade: se novas sujeiras aparecerem, pode mudar de plano

        Parâmetros:
        - posicao_atual: tupla (x, y) da posição atual do agente

        Define:
        - self.intentions: lista com UMA ação ['N'], ['S'], ['L'], ['O'], ou ['aspirar']
        """
        self.intentions = []

        # Se não há desires (rota), não faz nada
        if not self.desires:
            return

        # Pega o primeiro objetivo da rota
        proximo_objetivo = self.desires[0]
        coord_objetivo = proximo_objetivo["coord"]

        # Se já está no objetivo, aspira
        if posicao_atual == coord_objetivo:
            self.intentions = ["aspirar"]
            # Remove objetivo dos desires após aspirar
            self.desires.pop(0)
            return

        # Calcula próximo passo em direção ao objetivo
        direcao = self.calcular_proximo_passo(posicao_atual, coord_objetivo)

        if direcao:
            self.intentions = [direcao]
        else:
            # Se não há caminho, remove objetivo inacessível e tenta próximo
            self.desires.pop(0)
            # Tenta recalcular com próximo objetivo
            if self.desires:
                self.update_intentions(posicao_atual)
        


agente = Agente_BDI(tamanho=5)
x, y = 0,0

while agente.bateria > 0:
    agente.perceive((x, y))
    agente.update_desires((x,y))
    agente.update_intentions((x,y))
    if agente.intentions:
        acao = agente.intentions[0]
        if acao == "aspirar":
            agente.grid[x][y] = "limpo"
            agente.bateria -= 2
        elif acao == "N":
            x -= 1
            agente.bateria -= 1
        elif acao == "S":
            x += 1
            agente.bateria -= 1
        elif acao == "L":
            y += 1
            agente.bateria -= 1
        elif acao == "O":
            y -= 1
            agente.bateria -= 1
