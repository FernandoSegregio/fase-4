import os
import json
import oracledb
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
dsn = os.getenv('DB_DSN')

# Função para conectar ao banco de dados Oracle
def conectar_banco():
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        print("Conectado ao banco de dados")
        return conn
    except oracledb.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para inserir dados no banco de dados
def inserir_dados_banco(conn, dados):
    try:
        cursor = conn.cursor()
        for dado in dados:
            cursor.execute("""
                INSERT INTO Colheita (ano, quantidade_colhida) VALUES (:ano, :quantidade_colhida)""",
                ano=dado['ano'], quantidade_colhida=dado['quantidade_colhida']
            )
            cursor.execute("""
                INSERT INTO Clima (ano, temperatura_media, precipitacao) VALUES (:ano, :temperatura_media, :precipitacao)""",
                ano=dado['ano'], temperatura_media=dado['clima']['temperatura_media'], precipitacao=dado['clima']['precipitacao']
            )
            cursor.execute("""
                INSERT INTO MaturidadeCana (ano, indice_maturidade) VALUES (:ano, :indice_maturidade)""",
                ano=dado['ano'], indice_maturidade=dado['maturidade_cana']['indice_maturidade']
            )
            cursor.execute("""
                INSERT INTO CondicoesSolo (ano, ph, nutrientes) VALUES (:ano, :ph, :nutrientes)""",
                ano=dado['ano'], ph=dado['condicoes_solo']['ph'], nutrientes=dado['condicoes_solo']['nutrientes']
            )
        conn.commit()
        cursor.close()
        print("Dados inseridos com sucesso")
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")

# Função para alterar dados
def alterar_dados(conn):
    try:
        cursor = conn.cursor()
        ano = int(input("Digite o ano do registro que deseja alterar: "))
        
        # Verificar se o ano existe
        cursor.execute("SELECT * FROM Colheita WHERE ano = :ano", ano=ano)
        if cursor.fetchone() is None:
            print(f"Não há registros para o ano {ano}")
            return

        print("O que você deseja alterar?")
        print("1. Quantidade colhida")
        print("2. Dados climáticos")
        print("3. Índice de maturidade")
        print("4. Condições do solo")
        opcao = input("Escolha uma opção (1-4): ")

        if opcao == '1':
            nova_quantidade = float(input("Nova quantidade colhida: "))
            cursor.execute("UPDATE Colheita SET quantidade_colhida = :quantidade WHERE ano = :ano",
                           quantidade=nova_quantidade, ano=ano)
        elif opcao == '2':
            nova_temperatura = float(input("Nova temperatura média: "))
            nova_precipitacao = float(input("Nova precipitação: "))
            cursor.execute("UPDATE Clima SET temperatura_media = :temp, precipitacao = :prec WHERE ano = :ano",
                           temp=nova_temperatura, prec=nova_precipitacao, ano=ano)
        elif opcao == '3':
            novo_indice = float(input("Novo índice de maturidade: "))
            cursor.execute("UPDATE MaturidadeCana SET indice_maturidade = :indice WHERE ano = :ano",
                           indice=novo_indice, ano=ano)
        elif opcao == '4':
            novo_ph = float(input("Novo pH do solo: "))
            novos_nutrientes = float(input("Nova quantidade de nutrientes: "))
            cursor.execute("UPDATE CondicoesSolo SET ph = :ph, nutrientes = :nutrientes WHERE ano = :ano",
                           ph=novo_ph, nutrientes=novos_nutrientes, ano=ano)
        else:
            print("Opção inválida")
            return

        conn.commit()
        print("Dados alterados com sucesso")
    except oracledb.DatabaseError as e:
        print(f"Erro ao alterar dados: {e}")
    finally:
        cursor.close()

# Função para incluir novos dados
def incluir_dados(conn):
    try:
        ano = int(input("Ano: "))
        quantidade_colhida = float(input("Quantidade colhida: "))
        temperatura_media = float(input("Temperatura média: "))
        precipitacao = float(input("Precipitação: "))
        indice_maturidade = float(input("Índice de maturidade: "))
        ph = float(input("pH do solo: "))
        nutrientes = float(input("Quantidade de nutrientes: "))

        dados = [{
            "ano": ano,
            "quantidade_colhida": quantidade_colhida,
            "clima": {
                "temperatura_media": temperatura_media,
                "precipitacao": precipitacao
            },
            "maturidade_cana": {
                "indice_maturidade": indice_maturidade
            },
            "condicoes_solo": {
                "ph": ph,
                "nutrientes": nutrientes
            }
        }]

        inserir_dados_banco(conn, dados)
        print("Novos dados incluídos com sucesso")
    except ValueError:
        print("Erro: Por favor, insira valores numéricos válidos.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao incluir novos dados: {e}")

# Função para excluir um dado específico
def excluir_dado(conn):
    try:
        cursor = conn.cursor()
        ano = int(input("Digite o ano do registro que deseja excluir: "))
        
        # Verificar se o ano existe
        cursor.execute("SELECT * FROM Colheita WHERE ano = :ano", ano=ano)
        if cursor.fetchone() is None:
            print(f"Não há registros para o ano {ano}")
            return

        # Excluir dados de todas as tabelas relacionadas
        cursor.execute("DELETE FROM Colheita WHERE ano = :ano", ano=ano)
        cursor.execute("DELETE FROM Clima WHERE ano = :ano", ano=ano)
        cursor.execute("DELETE FROM MaturidadeCana WHERE ano = :ano", ano=ano)
        cursor.execute("DELETE FROM CondicoesSolo WHERE ano = :ano", ano=ano)

        conn.commit()
        print(f"Dados do ano {ano} excluídos com sucesso")
    except oracledb.DatabaseError as e:
        print(f"Erro ao excluir dados: {e}")
    finally:
        cursor.close()

# Função para excluir todos os dados
def excluir_todos_dados(conn):
    confirmacao = input("ATENÇÃO: Isso irá excluir TODOS os dados. Digite 'CONFIRMAR' para prosseguir: ")
    if confirmacao != 'CONFIRMAR':
        print("Operação cancelada")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Colheita")
        cursor.execute("DELETE FROM Clima")
        cursor.execute("DELETE FROM MaturidadeCana")
        cursor.execute("DELETE FROM CondicoesSolo")
        conn.commit()
        print("Todos os dados foram excluídos com sucesso")
    except oracledb.DatabaseError as e:
        print(f"Erro ao excluir todos os dados: {e}")
    finally:
        cursor.close()

# Nova função para listar arquivos JSON na pasta src
def listar_arquivos_json():
    pasta_src = 'src'
    arquivos_json = [f for f in os.listdir(pasta_src) if f.endswith('.json')]
    return arquivos_json

# Nova função para carregar dados de um arquivo JSON selecionado
def carregar_dados_json_selecionado(conn):
    arquivos_json = listar_arquivos_json()
    
    if not arquivos_json:
        print("Não há arquivos JSON na pasta 'src'.")
        return

    print("\nArquivos JSON disponíveis:")
    for i, arquivo in enumerate(arquivos_json, 1):
        print(f"{i}. {arquivo}")

    try:
        escolha = int(input("\nEscolha o número do arquivo que deseja carregar: ")) - 1
        if 0 <= escolha < len(arquivos_json):
            nome_arquivo = arquivos_json[escolha]
            caminho_arquivo = os.path.join('src', nome_arquivo)
            
            with open(caminho_arquivo, 'r') as arquivo:
                dados = json.load(arquivo)
            
            inserir_dados_banco(conn, dados)
            print(f"Dados do arquivo {nome_arquivo} carregados com sucesso")
        else:
            print("Escolha inválida.")
    except ValueError:
        print("Por favor, insira um número válido.")
    except FileNotFoundError:
        print(f"Erro: O arquivo {nome_arquivo} não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo {nome_arquivo} não é um JSON válido.")
    except Exception as e:
        print(f"Erro ao carregar dados do arquivo JSON: {e}")

# Função principal do menu
def menu_principal():
    conn = conectar_banco()
    if not conn:
        return

    while True:
        print("\n=== Menu Principal ===")
        print("1. Inserir dados simulados")
        print("2. Alterar dados")
        print("3. Incluir novos dados")
        print("4. Excluir um dado específico")
        print("5. Excluir todos os dados")
        print("6. Carregar dados de arquivo JSON")
        print("7. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            inserir_dados_banco(conn, gerar_dados_simulados())
        elif opcao == '2':
            alterar_dados(conn)
        elif opcao == '3':
            incluir_dados(conn)
        elif opcao == '4':
            excluir_dado(conn)
        elif opcao == '5':
            excluir_todos_dados(conn)
        elif opcao == '6':
            carregar_dados_json(conn)
        elif opcao == '7':
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

    conn.close()

# Função para gerar dados simulados
def gerar_dados_simulados():
    return [
        {
            "ano": 2021,
            "quantidade_colhida": 1500,
            "clima": {
                "temperatura_media": 25.3,
                "precipitacao": 1200
            },
            "maturidade_cana": {
                "indice_maturidade": 0.85
            },
            "condicoes_solo": {
                "ph": 6.5,
                "nutrientes": 0.75
            }
        },
        {
            "ano": 2022,
            "quantidade_colhida": 1600,
            "clima": {
                "temperatura_media": 26.1,
                "precipitacao": 1100
            },
            "maturidade_cana": {
                "indice_maturidade": 0.88
            },
            "condicoes_solo": {
                "ph": 6.4,
                "nutrientes": 0.78
            }
        },
        {
            "ano": 2023,
            "quantidade_colhida": 1550,
            "clima": {
                "temperatura_media": 25.8,
                "precipitacao": 1150
            },
            "maturidade_cana": {
                "indice_maturidade": 0.86
            },
            "condicoes_solo": {
                "ph": 6.6,
                "nutrientes": 0.76
            }
        }
    ]

# Executar o menu principal
if __name__ == "__main__":
    menu_principal()