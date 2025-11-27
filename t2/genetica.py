import random
from typing import List, Tuple, Optional
from puzzle import aplicar_movimento, distancia_manhattan

RECOMPENSA_POR_SOLUCAO = 1000000

def criar_individuo_aleatorio(tamanho: int, movimentos: List[str]) -> List:
    genes = []
    i = 0
    while i < tamanho:
        r = random.randint(0, len(movimentos) - 1)
        genes.append(movimentos[r])
        i += 1
    return [genes, None, None, None]

def avaliar_individuo(individuo: List, estado_inicial, objetivo, aplicar, dist_fn):
    estado = estado_inicial
    min_dist = None
    passo_do_min = 0
    estado_no_min = estado_inicial
    p = 0
    i = 0
    while i < len(individuo[0]):
        mov = individuo[0][i]
        estado = aplicar(estado, mov)
        p += 1
        d = dist_fn(estado)
        if min_dist is None:
            min_dist = d
            passo_do_min = p
            estado_no_min = estado
        else:
            if d < min_dist:
                min_dist = d
                passo_do_min = p
                estado_no_min = estado
        if estado == objetivo:
            individuo[2] = estado
            individuo[3] = p
            individuo[1] = RECOMPENSA_POR_SOLUCAO + (len(individuo[0]) - p)
            return individuo[1]
        i += 1

    individuo[2] = estado_no_min
    individuo[3] = None
    if min_dist is None:
        min_dist = dist_fn(estado_inicial)
        passo_do_min = 0
        estado_no_min = estado_inicial

    base = 1.0 / (1.0 + min_dist)
    bonus_rapidez = 0.0
    if passo_do_min > 0:
        bonus_rapidez = (len(individuo[0]) - passo_do_min) / (len(individuo[0]) * 100.0)
    individuo[1] = base + bonus_rapidez
    return individuo[1]

def fitness_eh_menor(a: List, b: List) -> bool:
    fa = a[1]
    fb = b[1]
    if fa is None and fb is None:
        return False
    if fa is None and fb is not None:
        return True
    if fb is None and fa is not None:
        return False
    return fa < fb

def ordenar_populacao(pop: List[List]) -> None:
    n = len(pop)
    i = 0
    while i < n - 1:
        m = i
        j = i + 1
        while j < n:
            if fitness_eh_menor(pop[j], pop[m]):
                m = j
            j += 1
        if m != i:
            temp = pop[i]
            pop[i] = pop[m]
            pop[m] = temp
        i += 1

def escolher_melhor(pop: List[List]) -> Optional[List]:
    if len(pop) == 0:
        return None
    i = 0
    melhor = None
    while i < len(pop):
        if pop[i][1] is not None:
            if melhor is None:
                melhor = pop[i]
            else:
                if pop[i][1] > melhor[1]:
                    melhor = pop[i]
        i += 1
    if melhor is None:
        return pop[0]
    return melhor

def torneio(pop: List[List], k: int) -> List:
    tam = len(pop)
    melhor = None
    x = 0
    while x < k:
        r = random.randint(0, tam - 1)
        ind = pop[r]
        if melhor is None:
            melhor = ind
        else:
            if ind[1] is not None and melhor[1] is not None:
                if ind[1] > melhor[1]:
                    melhor = ind
            elif melhor[1] is None and ind[1] is not None:
                melhor = ind
        x += 1
    return melhor

def cruzar(a: List, b: List) -> Tuple[List, List]:
    L = len(a[0])
    if L <= 1:
        return [a[0][:], None, None, None], [b[0][:], None, None, None]
    p = random.randint(1, L - 1)
    g1 = []
    g2 = []
    i = 0
    while i < p:
        g1.append(a[0][i])
        g2.append(b[0][i])
        i += 1
    while i < L:
        g1.append(b[0][i])
        g2.append(a[0][i])
        i += 1
    return [g1, None, None, None], [g2, None, None, None]

def mutar(ind: List, taxa: float, movimentos: List[str]):
    L = len(ind[0])
    i = 0
    while i < L:
        r = random.randint(0, 1000000)
        t = int(taxa * 1000000)
        if r < t:
            r2 = random.randint(0, len(movimentos) - 1)
            ind[0][i] = movimentos[r2]
        i += 1

def executar_ga(estado_inicial,
                objetivo,
                movimentos,
                tamanho_pop,
                tam_genes,
                geracoes,
                taxa_mut):

    pop = []
    i = 0
    while i < tamanho_pop:
        ind = criar_individuo_aleatorio(tam_genes, movimentos)
        avaliar_individuo(ind, estado_inicial, objetivo, aplicar_movimento, distancia_manhattan)
        pop.append(ind)
        i += 1

    melhor = escolher_melhor(pop)

    g = 1
    while g <= geracoes:
        j = 0
        while j < len(pop):
            if pop[j][3] is not None:
                passos = pop[j][3]
                seq = pop[j][0][:passos]
                return True, seq, g
            j += 1

        ordenar_populacao(pop)
        novos = []

        elites = 2
        if elites > len(pop):
            elites = len(pop)
        inicio = len(pop) - elites
        i = inicio
        while i < len(pop):
            genes = []
            k = 0
            while k < len(pop[i][0]):
                genes.append(pop[i][0][k])
                k += 1
            ind = [genes, None, None, None]
            avaliar_individuo(ind, estado_inicial, objetivo, aplicar_movimento, distancia_manhattan)
            novos.append(ind)
            i += 1

        while len(novos) < tamanho_pop:
            p1 = torneio(pop, 3)
            p2 = torneio(pop, 3)
            f1, f2 = cruzar(p1, p2)
            mutar(f1, taxa_mut, movimentos)
            mutar(f2, taxa_mut, movimentos)
            avaliar_individuo(f1, estado_inicial, objetivo, aplicar_movimento, distancia_manhattan)
            if len(novos) < tamanho_pop:
                novos.append(f1)
            avaliar_individuo(f2, estado_inicial, objetivo, aplicar_movimento, distancia_manhattan)
            if len(novos) < tamanho_pop:
                novos.append(f2)

        pop = novos
        atual = escolher_melhor(pop)
        if melhor is None:
            melhor = atual
        else:
            if atual is not None:
                if melhor[1] is None and atual[1] is not None:
                    melhor = atual
                elif melhor[1] is not None and atual[1] is not None:
                    if atual[1] > melhor[1]:
                        melhor = atual

        g += 1

    return False, [], 0