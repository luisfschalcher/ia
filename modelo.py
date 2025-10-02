from desenharMapa import inicializar_ambiente
from agente import aspiradorModelo
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np  

def sensores(grid, x, y):
    tamanho = len(grid)
    
    def pode_mover(nx, ny):
        if 0 <= nx < tamanho and 0 <= ny < tamanho and grid[nx][ny] != "movel":
            return True
        return False
    
    if pode_mover(x - 1, y):
        norte = 1
    else:
        norte = 0
    if pode_mover(x + 1, y):
        sul = 1
    else:
        sul = 0
    if pode_mover(x, y - 1):
        oeste = 1
    else: 
        oeste = 0
    if pode_mover(x, y + 1):
        leste = 1
    else:
        leste = 0
    est = grid[x][y]
    return norte, sul, leste, oeste, est

def sensoresPr(grid, x, y):
    sujeira = {"poeira", "liquido", "detritos"}
    prioridades = []
    tamanho = len(grid)

    def pode_mover(nx, ny):
        if 0 <= nx < tamanho and 0 <= ny < tamanho and grid[nx][ny] != "movel":
            return True
        return False

    if x + 1 < tamanho and pode_mover(x + 1, y) and grid[x + 1][y] in sujeira:
        prioridades.append('S')
    if x - 1 >= 0 and pode_mover(x - 1, y) and grid[x - 1][y] in sujeira:
        prioridades.append('N')
    if y + 1 < tamanho and pode_mover(x, y + 1) and grid[x][y + 1] in sujeira:
        prioridades.append('L')
    if y - 1 >= 0 and pode_mover(x, y - 1) and grid[x][y - 1] in sujeira:
        prioridades.append('O')

    return prioridades

def rodar_simulacao(tamanho=5, max_steps=60):
    grid = inicializar_ambiente(tamanho)
    x, y = 0, 0
    bateria = 30

    estados = []
    visitados = set()
    visitados.add((x, y))

    for _ in range(max_steps):
        norte, sul, leste, oeste, est = sensores(grid, x, y)
        prioridade = sensoresPr(grid, x, y)
        acao, bateria = aspiradorModelo(norte, sul, leste, oeste, est, bateria, prioridade, pos=(x, y), visitados=visitados)

        if acao == "aspirar":
            grid[x][y] = "limpo"
            visitados.add((x, y))
        elif acao == "S" and x < tamanho - 1:
            x += 1
            visitados.add((x, y))
        elif acao == "N" and x > 0:
            x -= 1
            visitados.add((x, y))
        elif acao == "L" and y < tamanho - 1:
            y += 1
            visitados.add((x, y))
        elif acao == "O" and y > 0:
            y -= 1
            visitados.add((x, y))
        elif acao == "parar":
            break

        estados.append({
            'grid': np.copy(grid),
            'x': x,
            'y': y,
            'bateria': bateria
        })

    return estados, grid

def simulacao():
    tamanho = 5
    estados, grid = rodar_simulacao(tamanho=tamanho, max_steps=60)

    if not estados:
        return

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xticks(np.arange(tamanho + 1) - 0.5)
    ax.set_yticks(np.arange(tamanho + 1) - 0.5)
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_xlim(-0.5, tamanho - 0.5)
    ax.set_ylim(-0.5, tamanho - 0.5)

    agent_marker = ax.plot([], [], 'o', markersize=20)[0]

    texts = [[None for _ in range(tamanho)] for _ in range(tamanho)]
    movel_patches = []

    def desenhar_estado_inicial():
        for i in range(tamanho):
            for j in range(tamanho):
                valor = grid[i][j]
                if valor == "poeira":
                    txt = 'P'
                    cor = 'brown'
                elif valor == "liquido":
                    txt = 'L'
                    cor = 'blue'
                elif valor == "detritos":
                    txt = 'D'
                    cor = 'black'
                elif valor == "movel":
                    rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color='gray')
                    ax.add_patch(rect)
                    movel_patches.append(rect)
                    txt = ''
                    cor = 'black'
                else:
                    txt = ''
                    cor = 'lightgray'

                texts[i][j] = ax.text(j, i, txt, ha='center', va='center',
                                      fontsize=14, color=cor, weight='bold')

    desenhar_estado_inicial()

    primeiro = estados[0]
    agent_marker.set_data([primeiro['y']], [primeiro['x']])

    def update(frame):
        estado = estados[frame]
        grid_atual = estado['grid']
        x, y = estado['x'], estado['y']

        for i in range(tamanho):
            for j in range(tamanho):
                cell = grid_atual[i][j]
                text_artist = texts[i][j]
                if cell == "limpo":
                    text_artist.set_text('.')
                    text_artist.set_color('gray')
                elif cell == "poeira":
                    text_artist.set_text('P')
                    text_artist.set_color('brown')
                elif cell == "liquido":
                    text_artist.set_text('L')
                    text_artist.set_color('blue')
                elif cell == "detritos":
                    text_artist.set_text('D')
                    text_artist.set_color('black')
                elif cell == "movel":
                    text_artist.set_text('')
                else:
                    text_artist.set_text('.')
                    text_artist.set_color('lightgray')

        agent_marker.set_data([y], [x])

        artists = [agent_marker] + [t for row in texts for t in row]
        return artists

    ani = FuncAnimation(fig, update, frames=len(estados), interval=500, blit=False, repeat=False)
    plt.show()