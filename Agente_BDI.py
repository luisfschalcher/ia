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
    
    def detecta_tipo_sujeira(self, sujeira):
        if sujeira == "poeira":
            return 1
        elif sujeira == "liquido":
            return 2
        else:
            return 3
    
    def perceive(self, posicao):
        """
        Detecta todas as sujeiras no grid (percepção global).
        Atualiza self.beliefs como lista de dicts {"coord": (x,y), "pontos": n}
        """
        sujeira = {"poeira", "liquido", "detritos"}
        self.beliefs = []  # reinicia beliefs
        linhas = len(self.grid)
        colunas = len(self.grid[0])

        for i in range(linhas):
            for j in range(colunas):
                if self.grid[i][j] in sujeira:
                    b = {"coord": (i, j), "pontos": self.detecta_tipo_sujeira(self.grid[i][j])}
                    self.beliefs.append(b)

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
        

def simular(tamanho=5, max_steps=100, intervalo_ms=500):
    agente = Agente_BDI(tamanho=tamanho)
    x, y = 0, 0

    estados = []
    total_pontuacao = 0

    for passo in range(max_steps):
        if agente.bateria <= 0:
            break

        agente.perceive((x, y))
        dedup = {}
        for b in agente.beliefs:
            dedup[b['coord']] = b
        agente.beliefs = list(dedup.values())

        agente.update_desires((x, y))
        agente.update_intentions((x, y))

        if not agente.intentions:
            break

        acao = agente.intentions[0]

        delta = 0
        if acao == "aspirar":
            conteudo = agente.grid[x][y]
            sujeira = {"poeira", "liquido", "detritos"}
            if conteudo in sujeira:
                delta = agente.detecta_tipo_sujeira(conteudo)
            agente.grid[x][y] = "limpo"
            agente.bateria -= 2
            agente.beliefs = [b for b in agente.beliefs if b['coord'] != (x, y)]
        elif acao == "N":
            if x > 0 and agente.pode_mover(x - 1, y):
                x -= 1
                agente.bateria -= 1
        elif acao == "S":
            if x < tamanho - 1 and agente.pode_mover(x + 1, y):
                x += 1
                agente.bateria -= 1
        elif acao == "L":
            if y < tamanho - 1 and agente.pode_mover(x, y + 1):
                y += 1
                agente.bateria -= 1
        elif acao == "O":
            if y > 0 and agente.pode_mover(x, y - 1):
                y -= 1
                agente.bateria -= 1
        else:
            break

        total_pontuacao += delta

        estados.append({
            'grid': np.copy(agente.grid),
            'x': x,
            'y': y,
            'bateria': agente.bateria,
            'pontuacao': total_pontuacao,
            'passo': passo
        })

    if not estados:
        print("Nenhum estado gerado")
        return

    fig, ax = plt.subplots(figsize=(5, 5))
    tamanho = len(estados[0]['grid'])
    ax.set_xticks(np.arange(tamanho + 1) - 0.5)
    ax.set_yticks(np.arange(tamanho + 1) - 0.5)
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_xlim(-0.5, tamanho - 0.5)
    ax.set_ylim(-0.5, tamanho - 0.5)

    agent_marker = ax.plot([], [], 'o', markersize=18)[0]
    score_text = ax.text(0.01, 0.99, "", transform=ax.transAxes, fontsize=12,
                         va='top', ha='left', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=4))

    texts = [[None for _ in range(tamanho)] for _ in range(tamanho)]
    movel_patches = []

    grid0 = estados[0]['grid']
    for i in range(tamanho):
        for j in range(tamanho):
            valor = grid0[i][j]
            if valor == "poeira":
                txt = 'P'; cor = 'brown'
            elif valor == "liquido":
                txt = 'L'; cor = 'blue'
            elif valor == "detritos":
                txt = 'D'; cor = 'black'
            elif valor == "movel":
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color='gray')
                ax.add_patch(rect)
                movel_patches.append(rect)
                txt = ''; cor = 'black'
            else:
                txt = '.'; cor = 'lightgray'
            texts[i][j] = ax.text(j, i, txt, ha='center', va='center', fontsize=14, color=cor, weight='bold')

    primeiro = estados[0]
    agent_marker.set_data([primeiro['y']], [primeiro['x']])
    score_text.set_text(f"Pontuação: {primeiro.get('pontuacao', 0)}  Bateria: {primeiro.get('bateria', 0)}")

    def update(frame):
        estado = estados[frame]
        grid_atual = estado['grid']
        x, y = estado['x'], estado['y']

        for i in range(tamanho):
            for j in range(tamanho):
                cell = grid_atual[i][j]
                t = texts[i][j]
                if cell == "limpo":
                    t.set_text('.'); t.set_color('gray')
                elif cell == "poeira":
                    t.set_text('P'); t.set_color('brown')
                elif cell == "liquido":
                    t.set_text('L'); t.set_color('blue')
                elif cell == "detritos":
                    t.set_text('D'); t.set_color('black')
                elif cell == "movel":
                    t.set_text('')
                else:
                    t.set_text('.'); t.set_color('lightgray')

        agent_marker.set_data([y], [x])

        score_text.set_text(f"Pontuação: {estado.get('pontuacao', 0)}  Bateria: {estado.get('bateria', 0)}")
        artists = [agent_marker, score_text] + [t for row in texts for t in row]
        return artists

    ani = FuncAnimation(fig, update, frames=len(estados), interval=intervalo_ms, blit=False, repeat=False)
    plt.show()