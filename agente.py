def aspiradorSimples(norte, sul, leste, oeste, est, bateria, prioridade=None):
    sujeira = {"poeira", "liquido", "detritos"}
    if bateria != 0:
        prioridade = prioridade or []
        if est in sujeira:
            bateria -= 2
            return "aspirar", bateria
        
        if 'S' in prioridade and sul == 1:
            bateria -= 1
            return "S", bateria
        if 'N' in prioridade and norte == 1:
            bateria -= 1
            return "N", bateria
        if 'L' in prioridade and leste == 1:
            bateria -= 1
            return "L", bateria
        if 'O' in prioridade and oeste == 1:
            bateria -= 1
            return "O", bateria
        
        if sul == 1:
            bateria -= 1
            return "S", bateria
        if norte == 1:
            bateria -= 1
            return "N", bateria
        if leste == 1:
            bateria -= 1
            return "L", bateria
        if oeste == 1:
            bateria -= 1
            return "O", bateria
        
    return "parar", bateria