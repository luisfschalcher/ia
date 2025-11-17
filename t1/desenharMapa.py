import numpy as np
import random
import matplotlib.pyplot as plt

def inicializar_ambiente(tamanho=5):
    grid = np.full((tamanho, tamanho), "limpo", dtype=object)
    ocupados = set()

    def posicao_livre():
        while True:
            x, y = random.randint(0, tamanho - 1), random.randint(0, tamanho - 1)
            if (x, y) not in ocupados:
                return x, y

    for i in range(2):
        x, y = posicao_livre()
        grid[x][y] = "poeira"
        ocupados.add((x, y))

    for i in range(2):
        x, y = posicao_livre()
        grid[x][y] = "liquido"
        ocupados.add((x, y))

    for i in range(2):
        x, y = posicao_livre()
        grid[x][y] = "detritos"
        ocupados.add((x, y))

    for i in range(2):
        colocado = False
        while not colocado:
            x, y = posicao_livre()
            direcao = random.choice(['H', 'V'])
            if direcao == 'H' and y < tamanho - 1 and (x, y + 1) not in ocupados:
                grid[x][y] = "movel"
                grid[x][y + 1] = "movel"
                ocupados.update({(x, y), (x, y + 1)})
                colocado = True
            elif direcao == 'V' and x < tamanho - 1 and (x + 1, y) not in ocupados:
                grid[x][y] = "movel"
                grid[x + 1][y] = "movel"
                ocupados.update({(x, y), (x + 1, y)})
                colocado = True

    return grid

def desenhar_grid(grid, pos=None):
    tamanho = len(grid)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xticks(np.arange(tamanho + 1) - 0.5)
    ax.set_yticks(np.arange(tamanho + 1) - 0.5)
    ax.grid(True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.invert_yaxis()

    for i in range(tamanho):
        for j in range(tamanho):
            if pos and (i, j) == pos:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color='lightblue'))

            valor = grid[i, j]
            if valor == "poeira":
                ax.text(j, i, 'P', ha='center', va='center', fontsize=16, color='brown', weight='bold')
            elif valor == "liquido":
                ax.text(j, i, 'L', ha='center', va='center', fontsize=16, color='blue', weight='bold')
            elif valor == "detritos":
                ax.text(j, i, 'D', ha='center', va='center', fontsize=16, color='black', weight='bold')
            elif valor == "movel":
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color='gray'))
            elif valor == "limpo":
                ax.text(j, i, '.', ha='center', va='center', fontsize=12, color='lightgray')

    plt.show()