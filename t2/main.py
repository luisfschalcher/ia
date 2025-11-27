import random
from typing import Tuple
from puzzle import eh_soluvel, aplicar_movimento, OBJETIVO
from genetica import executar_ga

Estado = Tuple[int, ...]

def gerar_estado():
    while True:
        lst = list(range(9))
        i = 0
        while i < 9:
            j = random.randint(0,8)
            tmp = lst[i]
            lst[i] = lst[j]
            lst[j] = tmp
            i += 1
        est = tuple(lst)
        if eh_soluvel(est) and est != OBJETIVO:
            return est

def imprimir_tabuleiro(estado: Estado) -> None:
    r = 0
    while r < 3:
        start = r * 3
        c = start
        linha = ""
        while c < start + 3:
            v = estado[c]
            if v == 0:
                linha = linha + "_"
            else:
                linha = linha + str(v)
            if c < start + 2:
                linha = linha + " "
            c += 1
        print(linha)
        r += 1

estado = gerar_estado()

print("Tabuleiro inicial:")
imprimir_tabuleiro(estado)

ok, seq, geracao = executar_ga(estado, OBJETIVO, ['U','D','L','R'], 200, 50, 2000, 0.04)

if ok:
    print()
    s = ""
    i = 0
    while i < len(seq):
        s = s + seq[i]
        i += 1
    print("Geração em que a solução foi encontrada:", geracao)
    print("Cromossomo (sequência de movimentos):", s)
    print()
    print("Estados do tabuleiro até a resolução:")
    atual = estado
    imprimir_tabuleiro(atual)
    print()
    i = 0
    while i < len(seq):
        mov = seq[i]
        atual = aplicar_movimento(atual, mov)
        print("Movimento:", mov)
        imprimir_tabuleiro(atual)
        print()
        i += 1
else:
    print("Não encontrou solução.")