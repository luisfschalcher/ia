def aspiradorSimples(norte, sul, leste, oeste, est, bateria, prioridade=None):
    pontuacao = 0
    sujeira = {"poeira", "liquido", "detritos"}
    if bateria != 0:
        prioridade = prioridade or []
        if est in sujeira:
            if est == "poeira":
                pontuacao += 1
            elif est == "liquido":
                pontuacao += 2
            else:
                pontuacao += 3
            bateria -= 2
            return "aspirar", bateria, pontuacao
        
        if 'S' in prioridade and sul == 1:
            bateria -= 1
            return "S", bateria, pontuacao
        if 'N' in prioridade and norte == 1:
            bateria -= 1
            return "N", bateria, pontuacao
        if 'L' in prioridade and leste == 1:
            bateria -= 1
            return "L", bateria, pontuacao
        if 'O' in prioridade and oeste == 1:
            bateria -= 1
            return "O", bateria, pontuacao
        
        if sul == 1:
            bateria -= 1
            return "S", bateria, pontuacao
        if norte == 1:
            bateria -= 1
            return "N", bateria, pontuacao
        if leste == 1:
            bateria -= 1
            return "L", bateria, pontuacao
        if oeste == 1:
            bateria -= 1
            return "O", bateria, pontuacao
        
    return "parar", bateria, pontuacao

def aspiradorModelo(norte, sul, leste, oeste, est, bateria, prioridade=None, pos=None, visitados=None):
    pontuacao = 0
    sujeira = {"poeira", "liquido", "detritos"}

    if bateria <= 0:
        return "parar", bateria, pontuacao

    prioridade = prioridade or []
    visitados = visitados or set()
    pos = pos or (None, None)
    x, y = pos

    def alvo(d):
        if d == 'S':
            return (x + 1, y)
        if d == 'N':
            return (x - 1, y)
        if d == 'L':
            return (x, y + 1)
        if d == 'O':
            return (x, y - 1)
        return None

    if est in sujeira:
        if est == "poeira":
            pontuacao += 1
        elif est == "liquido":
            pontuacao += 2
        else:
            pontuacao += 3
        bateria -= 2
        if pos is not None:
            visitados.add(pos)
        return "aspirar", bateria, pontuacao

    for d in prioridade:
        if d == 'S' and sul == 1:
            alvo = alvo('S')
            if alvo not in visitados:
                bateria -= 1
                return "S", bateria, pontuacao
        if d == 'N' and norte == 1:
            alvo = alvo('N')
            if alvo not in visitados:
                bateria -= 1
                return "N", bateria, pontuacao
        if d == 'L' and leste == 1:
            alvo = alvo('L')
            if alvo not in visitados:
                bateria -= 1
                return "L", bateria, pontuacao
        if d == 'O' and oeste == 1:
            alvo = alvo('O')
            if alvo not in visitados:
                bateria -= 1
                return "O", bateria, pontuacao

    for d in prioridade:
        if d == 'S' and sul == 1:
            bateria -= 1
            return "S", bateria, pontuacao
        if d == 'N' and norte == 1:
            bateria -= 1
            return "N", bateria, pontuacao
        if d == 'L' and leste == 1:
            bateria -= 1
            return "L", bateria, pontuacao
        if d == 'O' and oeste == 1:
            bateria -= 1
            return "O", bateria, pontuacao

    nao_visitados = []
    if sul == 1:
        nao_visitados.append(('S', alvo('S')))
    if norte == 1:
        nao_visitados.append(('N', alvo('N')))
    if leste == 1:
        nao_visitados.append(('L', alvo('L')))
    if oeste == 1:
        nao_visitados.append(('O', alvo('O')))

    for d, alvo in nao_visitados:
        if alvo not in visitados:
            bateria -= 1
            return d, bateria, pontuacao

    for d, alvo in nao_visitados:
        bateria -= 1
        return d, bateria, pontuacao

    return "parar", bateria, pontuacao