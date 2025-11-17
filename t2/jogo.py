"""
    - O algoritmo recebe um estado inicial (tupla de 9 inteiros, 0 = vazio) e tenta
      produzir uma sequência de movimentos (U,D,L,R) que leve ao estado final
      (1,2,3,4,5,6,7,8,0).
Notas:
    - Este GA usa cromossomos como sequências fixas de movimentos.
    - Movimentos inválidos (por ex., mover para fora do tabuleiro) são ignorados
      durante a simulação (tratados como no-op).
    - Fitness principal: distância de Manhattan do estado final; soluções alcançam
      fitness muito alta e interrompem a busca.
    - O código prioriza legibilidade e facilidade de ajuste de parâmetros.
"""
from typing import List, Tuple
import random
import time

State = Tuple[int, ...]  # tupla de 9 inteiros 0..8, 0 == vazio
MOVES = ['U', 'D', 'L', 'R']
GOAL: State = (1,2,3,4,5,6,7,8,0)

# --- Funções utilitárias do puzzle ---

def index_to_rc(idx: int) -> Tuple[int,int]:
    return divmod(idx, 3)  # (row, col)

def rc_to_index(r: int, c: int) -> int:
    return r * 3 + c

def apply_move(state: State, move: str) -> State:
    """Aplica um único movimento. Se inválido, retorna estado sem alteração."""
    zero_idx = state.index(0)
    r, c = index_to_rc(zero_idx)
    if move == 'U':
        nr, nc = r - 1, c
    elif move == 'D':
        nr, nc = r + 1, c
    elif move == 'L':
        nr, nc = r, c - 1
    elif move == 'R':
        nr, nc = r, c + 1
    else:
        return state
    if 0 <= nr < 3 and 0 <= nc < 3:
        nidx = rc_to_index(nr, nc)
        lst = list(state)
        lst[zero_idx], lst[nidx] = lst[nidx], lst[zero_idx]
        return tuple(lst)
    else:
        return state  # movimento inválido -> no-op

def apply_moves(state: State, moves: List[str]) -> State:
    s = state
    for m in moves:
        s = apply_move(s, m)
    return s

def manhattan(s: State) -> int:
    dist = 0
    for idx, val in enumerate(s):
        if val == 0:
            continue
        target_idx = val - 1
        r1, c1 = index_to_rc(idx)
        r2, c2 = index_to_rc(target_idx)
        dist += abs(r1 - r2) + abs(c1 - c2)
    return dist

def is_solvable(state: State) -> bool:
    """Verifica se um estado do 8-puzzle é solúvel usando inversões."""
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    # Para tabuleiro 3x3, solvable se inversões par
    return inv % 2 == 0

# --- Representação do GA ---

class Chromosome:
    def __init__(self, genes: List[str]):
        self.genes = genes
        self.fitness = None  # calculado sob demanda
        self.result_state = None  # estado resultante após aplicar genes
        self.steps_to_solution = None  # número de passos até alcançar a solução (se alcançado)

    def evaluate(self, start: State):
        """Aplica os genes a partir de `start`, calcula fitness e guarda estado resultante."""
        s = start
        steps = 0
        for g in self.genes:
            s = apply_move(s, g)
            steps += 1
            if s == GOAL:
                break
        self.result_state = s
        self.steps_to_solution = steps if s == GOAL else None
        d = manhattan(s)
        # Fitness: maior é melhor. Premia soluções e aproximação por Manhattan.
        if s == GOAL:
            # alcançou a solução: fitness muito alto, preferindo soluções em menos passos
            self.fitness = 1e9 - steps
        else:
            # transformar distância em valor positivo: quanto menor a distância, maior o fitness
            self.fitness = 1.0 / (1 + d)
        return self.fitness

# --- Operadores do GA ---

def random_gene() -> str:
    return random.choice(MOVES)

def make_random_chromosome(length: int) -> Chromosome:
    return Chromosome([random_gene() for _ in range(length)])

def tournament_select(pop: List[Chromosome], k: int = 3) -> Chromosome:
    aspirants = random.sample(pop, k)
    aspirants.sort(key=lambda c: c.fitness, reverse=True)
    return aspirants[0]

def one_point_crossover(a: Chromosome, b: Chromosome) -> Tuple[Chromosome, Chromosome]:
    L = len(a.genes)
    if L <= 1:
        return Chromosome(a.genes[:]), Chromosome(b.genes[:])
    p = random.randint(1, L-1)
    g1 = a.genes[:p] + b.genes[p:]
    g2 = b.genes[:p] + a.genes[p:]
    return Chromosome(g1), Chromosome(g2)

def mutate(chromo: Chromosome, pmut: float) -> None:
    L = len(chromo.genes)
    for i in range(L):
        if random.random() < pmut:
            chromo.genes[i] = random_gene()

def run_ga(start: State,
           pop_size: int = 200,
           gene_length: int = 40,
           generations: int = 2000,
           pmut: float = 0.03,
           elitism: int = 2,
           tournament_k: int = 3,
           seed: int = None,
           verbose: bool = True) -> Tuple[bool, List[str], dict]:
    """
   Retorna (found, moves, info)
      - found: bool indicando se solução foi encontrada
      - moves: lista de movimentos que resolvem (vazia se não achou)
      - info: dicionário com dados sobre a execução (melhor estado, fitness, tempo, gerações)
    """
    if seed is not None:
        random.seed(seed)

    assert is_solvable(start), "Estado inicial não é resolvível"

    start_time = time.time()

    # inicializa população
    population = [make_random_chromosome(gene_length) for _ in range(pop_size)]
    # avalia
    for c in population:
        c.evaluate(start)

    best_overall = max(population, key=lambda c: c.fitness)

    if verbose:
        print(f"Início GA: pop={pop_size} gene_len={gene_length} generations={generations}")
        print(f"Estado inicial: {start}")

    for gen in range(1, generations+1):
        # checar solução
        solved = [c for c in population if c.result_state == GOAL]
        if solved:
            best = min(solved, key=lambda c: c.steps_to_solution)
            elapsed = time.time() - start_time
            if verbose:
                print(f"Solução encontrada na geração {gen} (steps {best.steps_to_solution}) em {elapsed:.2f}s")
            return True, best.genes[:best.steps_to_solution], {
                'generations': gen,
                'time': elapsed,
                'best_fitness': best.fitness,
                'best_genes_full': best.genes,
            }

        # reprodução
        new_pop: List[Chromosome] = []
        # elitismo: mantém os melhores
        population.sort(key=lambda c: c.fitness, reverse=True)
        elites = population[:elitism]
        # copiar elites para nova população (e avaliar as cópias)
        for e in elites:
            copy = Chromosome(e.genes[:])
            copy.evaluate(start)         # <<< importante: calcula fitness/result_state
            new_pop.append(copy)

        # produzir o resto
        while len(new_pop) < pop_size:
            parent1 = tournament_select(population, k=tournament_k)
            parent2 = tournament_select(population, k=tournament_k)
            child1, child2 = one_point_crossover(parent1, parent2)
            mutate(child1, pmut)
            mutate(child2, pmut)
            child1.evaluate(start)
            if len(new_pop) < pop_size:
                new_pop.append(child1)
            if len(new_pop) < pop_size:
                child2.evaluate(start)
                new_pop.append(child2)

        population = new_pop

        # atualizar melhor
        current_best = max(population, key=lambda c: c.fitness)
        if current_best.fitness > best_overall.fitness:
            best_overall = current_best

        if verbose and gen % 50 == 0:
            elapsed = time.time() - start_time
            print(f"Gen {gen:4d} | Best fitness {best_overall.fitness:.6g} | Manh = {manhattan(best_overall.result_state)} | elapsed {elapsed:.1f}s")

    # fim das gerações
    elapsed = time.time() - start_time
    if verbose:
        print(f"Não foi encontrada solução após {generations} gerações (tempo {elapsed:.2f}s).")
        print(f"Melhor Estado (Manhattan={manhattan(best_overall.result_state)}): {best_overall.result_state}")
    return False, [], {
        'generations': generations,
        'time': elapsed,
        'best_fitness': best_overall.fitness,
        'best_state': best_overall.result_state,
        'best_genes_full': best_overall.genes,
    }

# --- Funções auxiliares para apresentação ---

def pretty_print_state(s: State) -> None:
    for r in range(3):
        row = s[r*3:(r+1)*3]
        print(' '.join(str(x) if x != 0 else '_' for x in row))

def moves_to_states(start: State, moves: List[str]) -> List[State]:
    s = start
    res = [s]
    for m in moves:
        s = apply_move(s, m)
        res.append(s)
    return res

if __name__ == '__main__':
    random.seed(1)
    while True:
        perm = list(range(9))
        random.shuffle(perm)
        start_state = tuple(perm)
        if is_solvable(start_state) and start_state != GOAL:
            break

    pretty_print_state(start_state)

    found, moves, info = run_ga(start_state,
                               pop_size=200,
                               gene_length=50,
                               generations=2000,
                               pmut=0.04,
                               elitism=4,
                               tournament_k=3,
                               seed=42,
                               verbose=True)

    if found:
        print("Sequência de movimentos que resolve (U,D,L,R):")
        print(''.join(moves))
        print("Caminho:")
        states = moves_to_states(start_state, moves)
        for s in states:
            pretty_print_state(s)
            print()
    else:
        print("Tente aumentar gene_length/pop_size/generations ou ajustar parâmetros.")