import re
import matplotlib.pyplot as plt

def analisar_hand_history(caminho_arquivo):
    # Lê o arquivo de texto com as mãos
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        texto = f.read()

    # Divide o texto separando cada mão individualmente
    hands = texto.split('CoinPoker Hand #')
    
    # Variáveis para armazenar o progresso das linhas do gráfico
    winnings_totais = [0]
    winnings_sd = [0]
    winnings_nsd = [0]
    
    total = 0
    sd_total = 0
    nsd_total = 0
    
    for hand in hands[1:]:
        investido = 0.0
        retornado = 0.0
        
        # Pula se o Hero não recebeu cartas nesta mão
        if 'Dealt to Hero' not in hand:
            continue
            
        linhas = hand.strip().split('\n')
        
        is_showdown = False
        hero_foi_pro_showdown = True
        
        # Verifica se a mão foi até o showdown e as cartas foram mostradas/escondidas na mesa
        if 'shows [' in hand or 'mucks hand' in hand:
            if re.search(r'Hero: folds', hand):
                hero_foi_pro_showdown = False
            else:
                is_showdown = True
        else:
            hero_foi_pro_showdown = False
        
        # Analisa cada ação linha por linha
        for linha in linhas:
            # Dinheiro que o Hero colocou no pote
            if linha.startswith('Hero: posts') or linha.startswith('Hero: bets') or linha.startswith('Hero: calls'):
                match = re.search(r'₮([\d.]+)', linha)
                if match:
                    investido += float(match.group(1))
            elif linha.startswith('Hero: raises'):
                # Em raises, o CoinPoker mostra "raises ₮X to ₮Y", sendo X o valor adicionado na ação
                match = re.search(r'raises ₮([\d.]+) to', linha)
                if match:
                    investido += float(match.group(1))
            
            # Dinheiro que retornou para o Hero (potes ganhos ou apostas não pagas devolvidas)
            elif linha.startswith('Hero: RETURN'):
                match = re.search(r'₮([\d.]+)', linha)
                if match:
                    retornado += float(match.group(1))
            elif linha.startswith('Hero collected'):
                match = re.search(r'₮([\d.]+)', linha)
                if match:
                    retornado += float(match.group(1))
        
        # Lucro líquido da mão atual
        net_profit = retornado - investido
        total += net_profit
        
        # Separa o lucro na linha correta (Showdown vs Non-Showdown)
        if is_showdown and hero_foi_pro_showdown:
            sd_total += net_profit
        else:
            nsd_total += net_profit
            
        winnings_totais.append(total)
        winnings_sd.append(sd_total)
        winnings_nsd.append(nsd_total)
        
    return winnings_totais, winnings_sd, winnings_nsd

# Executa a função apontando para o seu arquivo de texto
arquivo_txt = 'hands.txt' 
wt, wsd, wnsd = analisar_hand_history(arquivo_txt)

# Configuração e plotagem do gráfico
plt.figure(figsize=(10, 6))
plt.plot(wt, label='Dinheiro Ganho (Net Won)', color='green', linewidth=2.5)
plt.plot(wsd, label='EV Showdown / Showdown', color='blue', linewidth=1.5)
plt.plot(wnsd, label='Not Showdown (Red Line)', color='red', linewidth=1.5)

# Estilização visual
plt.title('Gráfico de Poker - HUD Caseiro')
plt.xlabel('Mãos Jogadas')
plt.ylabel('Lucro Acumulado (₮)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.axhline(0, color='black', linewidth=1.2) # Linha do zero (Breakeven)
plt.tight_layout()

# Exibe a janela com o gráfico final
plt.show()
