import os
import json
import oracledb
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime

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
def carregar_dados_json(conn):
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

#Treinamento Machine Learning
# Função para carregar dados do banco de dados para um DataFrame
def carregar_dados_db(conn):
    try:
        query = """
        SELECT c.ano, c.quantidade_colhida, cl.temperatura_media, cl.precipitacao, 
               m.indice_maturidade, s.ph, s.nutrientes
        FROM Colheita c
        JOIN Clima cl ON c.ano = cl.ano
        JOIN MaturidadeCana m ON c.ano = m.ano
        JOIN CondicoesSolo s ON c.ano = s.ano
        """
        df = pd.read_sql(query, conn)
        return df
    except oracledb.DatabaseError as e:
        print(f"Erro ao carregar dados do banco: {e}")
        return None

# Função para preparar os dados para o modelo
def preparar_dados(df):
    X = df[['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes']]
    y = df['quantidade_colhida']
    return X, y

# Função para treinar o modelo de machine learning
def treinar_modelo(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    previsoes = modelo.predict(X_test)
    erro = mean_squared_error(y_test, previsoes, squared=False)
    print(f'Erro médio absoluto: {erro:.2f} toneladas')
    
    return modelo

# Função para fazer previsões
def fazer_previsao(modelo, conn):
    print("\nInsira os dados para a previsão:")
    temperatura = float(input("Temperatura média: "))
    precipitacao = float(input("Precipitação: "))
    indice_maturidade = float(input("Índice de maturidade: "))
    ph = float(input("pH do solo: "))
    nutrientes = float(input("Quantidade de nutrientes: "))

    dados_previsao = pd.DataFrame([[temperatura, precipitacao, indice_maturidade, ph, nutrientes]], 
                                  columns=['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes'])
    
    previsao = modelo.predict(dados_previsao)
    print(f"\nPrevisão de colheita: {previsao[0]:.2f} toneladas")

# Função principal do menu atualizada
def menu_principal():
    conn = conectar_banco()
    if not conn:
        return

    modelo = None

    while True:
        print("\n=== Menu Principal ===")
        print("1. Inserir dados simulados")
        print("2. Alterar dados")
        print("3. Incluir novos dados")
        print("4. Excluir um dado específico")
        print("5. Excluir todos os dados")
        print("6. Carregar dados de arquivo JSON")
        print("7. Treinar modelo de previsão")
        print("8. Fazer previsão de colheita")
        print("9. Sair")

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
            df = carregar_dados_db(conn)
            if df is not None and not df.empty:
                X, y = preparar_dados(df)
                modelo = treinar_modelo(X, y)
                print("Modelo treinado com sucesso!")
            else:
                print("Não há dados suficientes para treinar o modelo.")
        elif opcao == '8':
            if modelo is None:
                print("Primeiro treine o modelo usando a opção 7.")
            else:
                fazer_previsao(modelo, conn)
        elif opcao == '9':
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

    conn.close()


# Função para agendar colheita
def agendar_colheita(conn):
    try:
        cursor = conn.cursor()
        plantacao_id = int(input("ID da plantação: "))
        data_colheita = input("Data da colheita (YYYY-MM-DD): ")
        
        # Validar o formato da data
        try:
            datetime.strptime(data_colheita, '%Y-%m-%d')
        except ValueError:
            print("Formato de data inválido. Use YYYY-MM-DD.")
            return

        sql = "INSERT INTO agendamentos (plantacao_id, data_colheita) VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'))"
        cursor.execute(sql, (plantacao_id, data_colheita))
        conn.commit()
        print("Colheita agendada com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao agendar colheita: {e}")
    finally:
        cursor.close()

# Função para listar agendamentos
def listar_agendamentos(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT plantacao_id, TO_CHAR(data_colheita, 'YYYY-MM-DD') FROM agendamentos ORDER BY data_colheita")
        agendamentos = cursor.fetchall()
        if agendamentos:
            print("\nAgendamentos de Colheita:")
            for row in agendamentos:
                print(f"Plantação ID: {row[0]}, Data Colheita: {row[1]}")
        else:
            print("Não há agendamentos de colheita.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao listar agendamentos: {e}")
    finally:
        cursor.close()

# Função para alocar recursos
def alocar_recursos(conn):
    try:
        cursor = conn.cursor()
        plantacao_id = int(input("ID da plantação: "))
        tipo_recurso = input("Tipo de recurso (ex: colhedora, trator): ")
        quantidade = int(input("Quantidade: "))
        
        sql = "INSERT INTO recursos_alocados (plantacao_id, tipo_recurso, quantidade) VALUES (:1, :2, :3)"
        cursor.execute(sql, (plantacao_id, tipo_recurso, quantidade))
        conn.commit()
        print("Recursos alocados com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao alocar recursos: {e}")
    finally:
        cursor.close()

# Função para listar recursos alocados
def listar_recursos_alocados(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT plantacao_id, tipo_recurso, quantidade FROM recursos_alocados")
        recursos = cursor.fetchall()
        if recursos:
            print("\nRecursos Alocados:")
            for row in recursos:
                print(f"Plantação ID: {row[0]}, Tipo: {row[1]}, Quantidade: {row[2]}")
        else:
            print("Não há recursos alocados.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao listar recursos alocados: {e}")
    finally:
        cursor.close()

# Função para criar gráficos
def criar_graficos(conn):
    try:
        df = carregar_dados_db(conn)
        if df is None or df.empty:
            print("Não há dados suficientes para criar gráficos.")
            return

        # Gráfico de linha para quantidade colhida ao longo dos anos
        plt.figure(figsize=(10, 6))
        plt.plot(df['ano'], df['quantidade_colhida'], marker='o')
        plt.title('Quantidade Colhida ao Longo dos Anos')
        plt.xlabel('Ano')
        plt.ylabel('Quantidade Colhida')
        plt.grid(True)
        plt.savefig('nome_do_arquivo.png')

        # Gráfico de barras para temperatura média e precipitação
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()
        ax1.bar(df['ano'], df['temperatura_media'], color='r', alpha=0.5, label='Temperatura Média')
        ax2.bar(df['ano'], df['precipitacao'], color='b', alpha=0.5, label='Precipitação')
        ax1.set_xlabel('Ano')
        ax1.set_ylabel('Temperatura Média (°C)', color='r')
        ax2.set_ylabel('Precipitação (mm)', color='b')
        plt.title('Temperatura Média e Precipitação por Ano')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        plt.savefig('nome_do_arquivo.png')

        # Gráfico de dispersão para relação entre índice de maturidade e quantidade colhida
        plt.figure(figsize=(10, 6))
        plt.scatter(df['indice_maturidade'], df['quantidade_colhida'])
        plt.title('Relação entre Índice de Maturidade e Quantidade Colhida')
        plt.xlabel('Índice de Maturidade')
        plt.ylabel('Quantidade Colhida')
        plt.grid(True)
        plt.savefig('nome_do_arquivo.png')

    except Exception as e:
        print(f"Erro ao criar gráficos: {e}")

# Função principal do menu atualizada
def menu_principal():
    conn = conectar_banco()
    if not conn:
        return

    modelo = None

    while True:
        print("\n=== Menu Principal ===")
        print("1. Inserir dados simulados")
        print("2. Alterar dados")
        print("3. Incluir novos dados")
        print("4. Excluir um dado específico")
        print("5. Excluir todos os dados")
        print("6. Carregar dados de arquivo JSON")
        print("7. Treinar modelo de previsão")
        print("8. Fazer previsão de colheita")
        print("9. Agendar colheita")
        print("10. Listar agendamentos de colheita")
        print("11. Alocar recursos")
        print("12. Listar recursos alocados")
        print("13. Criar gráficos")  
        print("14. Sair")

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
            df = carregar_dados_db(conn)
            if df is not None and not df.empty:
                X, y = preparar_dados(df)
                modelo = treinar_modelo(X, y)
                print("Modelo treinado com sucesso!")
            else:
                print("Não há dados suficientes para treinar o modelo.")
        elif opcao == '8':
            if modelo is None:
                print("Primeiro treine o modelo usando a opção 7.")
            else:
                fazer_previsao(modelo, conn)
        elif opcao == '9':
            agendar_colheita(conn)
        elif opcao == '10':
            listar_agendamentos(conn)
        elif opcao == '11':
            alocar_recursos(conn)
        elif opcao == '12':
            listar_recursos_alocados(conn)
        elif opcao == '13':
            criar_graficos(conn)
        elif opcao == '14':
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

    conn.close()

# Executar o menu principal
if __name__ == "__main__":
    menu_principal()