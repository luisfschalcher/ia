from typing import List, Tuple

Estado = Tuple[int, ...]

MOVES = ['U', 'D', 'L', 'R']

OBJETIVO: Estado = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def indice_para_rc(indice: int) -> Tuple[int, int]:
    return indice // 3, indice % 3

def rc_para_indice(r: int, c: int) -> int:
    return r * 3 + c

def aplicar_movimento(estado: Estado, mov: str) -> Estado:
    zero = estado.index(0)
    linha, coluna = indice_para_rc(zero)

    nova_linha = linha
    nova_coluna = coluna

    if mov == 'U':
        nova_linha = linha - 1
    elif mov == 'D':
        nova_linha = linha + 1
    elif mov == 'L':
        nova_coluna = coluna - 1
    elif mov == 'R':
        nova_coluna = coluna + 1
    else:
        return estado

    if nova_linha not in range(3) or nova_coluna not in range(3):
        return estado

    novo_indice = rc_para_indice(nova_linha, nova_coluna)
    lista = list(estado)
    lista[zero], lista[novo_indice] = lista[novo_indice], lista[zero]
    return tuple(lista)

def aplicar_sequencia(estado: Estado, seq: List[str]) -> Estado:
    s = estado
    i = 0
    while i < len(seq):
        s = aplicar_movimento(s, seq[i])
        i += 1
    return s

def distancia_manhattan(estado: Estado) -> int:
    soma = 0
    i = 0
    while i < 9:
        v = estado[i]
        if v != 0:
            alvo = v - 1
            r1, c1 = indice_para_rc(i)
            r2, c2 = indice_para_rc(alvo)
            dr = r1 - r2
            if dr < 0:
                dr = -dr
            dc = c1 - c2
            if dc < 0:
                dc = -dc
            soma += dr + dc
        i += 1
    return soma

def eh_resolvido(estado: Estado) -> bool:
    return estado == OBJETIVO

def eh_soluvel(estado: Estado) -> bool:
    arr = []
    i = 0
    while i < 9:
        if estado[i] != 0:
            arr.append(estado[i])
        i += 1
    inv = 0
    i = 0
    while i < len(arr):
        j = i + 1
        while j < len(arr):
            if arr[i] > arr[j]:
                inv += 1
            j += 1
        i += 1
    return inv % 2 == 0