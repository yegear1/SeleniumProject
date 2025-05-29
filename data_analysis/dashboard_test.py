import requests
import json
import pandas as pd
import os # Essencial para verificar a existência do arquivo

# --- Configuração ---
# AVISO: O código no meio da URL (qUyCEp...) é temporário e mudará,
# fazendo com que este link direto pare de funcionar no futuro.
name = "3060"
url = f"https://bestvaluegpu.com/_next/data/qUyCEpFqNx_bdUOLJ_peB/en-us/history/new-and-used-rtx-{name}-price-history-and-specs.json?slug=new-and-used-rtx-{name}-price-history-and-specs"

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

def collect_and_save_data():
    """
    Função principal que busca, processa e salva os dados em um único fluxo.
    """
    try:
        # 1. BUSCAR OS DADOS
        print(f"Buscando dados para RTX-{name}...")
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro se a requisição falhar (ex: 404)
        data = response.json()
        print("-> Dados recebidos com sucesso.")

        # 2. PROCESSAR OS DADOS
        prices = data["pageProps"]["last12MonthsChart"]
        price_data = [
            # Seleciona apenas as colunas que vamos usar no arquivo final
            [name, f"{entry['year']}-{MONTH_MAP[entry['month']]}-01", float(entry["new"])]
            for entry in prices
        ]
        
        # Cria o DataFrame final diretamente com as colunas certas
        df_final = pd.DataFrame(price_data, columns=['Modelo', 'Data', 'Preco'])
        print("-> DataFrame processado em memória:")
        print(df_final.head())

        # 3. SALVAR OU ANEXAR AO ARQUIVO CSV
        nome_arquivo_saida = 'gpu_data.csv'
        
        # Verifica se o arquivo já existe para decidir sobre o cabeçalho
        arquivo_existe = os.path.exists(nome_arquivo_saida)
        
        print(f"-> Tentando salvar/anexar em '{nome_arquivo_saida}'...")
        
        df_final.to_csv(
            nome_arquivo_saida,
            mode='a',             # 'a' para anexar (append)
            header=not arquivo_existe, # Só escreve o cabeçalho se o arquivo NÃO existir
            index=False           # Não escreve o índice do pandas
        )
        
        print(f"SUCESSO! Dados foram salvos em '{nome_arquivo_saida}'.")

    except requests.exceptions.RequestException as e:
        print(f"ERRO DE REDE: Não foi possível baixar os dados. {e}")
    except KeyError as e:
        print(f"ERRO NO JSON: A estrutura dos dados mudou. Chave não encontrada: {e}")
    except Exception as e:
        # Este 'except' genérico agora pegará QUALQUER erro, incluindo na hora de salvar
        print(f"ERRO INESPERADO: Ocorreu uma falha. Mensagem: {e}")

# --- Executa a função ---
collect_and_save_data()