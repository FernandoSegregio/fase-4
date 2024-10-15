import logging
from datetime import datetime

from scripts.connect_db import conectar_banco, fechar_conexao
from scripts.setup_db import setup_banco_dados
from scripts.consulta_banco import carregar_dados_db

from func_auxiliar import input_float
from gerador_de_graficos import criar_graficos
from dados_simulados import gerar_dados_simulados
from machine_learning import treinar_modelo
from machine_learning import preparar_dados
from machine_learning import fazer_previsao
from func_auxiliar import validar_ano

from gerenciador import GerenciadorDados
from gerenciador import DadosCompletos
from gerenciador import Colheita
from gerenciador import MaturidadeCana
from gerenciador import Clima
from gerenciador import CondicoesSolo


# Configuração de logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
    
#Função do menu principal
def menu_principal():
    """
    Função principal que exibe o menu e gerencia as interações do usuário.
    """ 
    conn = None
    try:
        conn = conectar_banco()
        if not conn:
            logging.error("Não foi possível conectar ao banco de dados. Encerrando o programa.")
            return

        setup_banco_dados(conn)
        gerenciador = GerenciadorDados()
        modelo = None

        while True:
            print("\n=== Menu Principal ===")
            print("1. Inserir dados simulados")
            print("2. Alterar dados")
            print("3. Incluir novos dados")
            print("4. Excluir um dado específico")
            print("5. Excluir todos os dados")
            print("6. Carregar dados de arquivo JSON")
            print("7. Carregar dados do banco")
            print("8. Treinar modelo de previsão")
            print("9. Fazer previsão de colheita")
            print("10. Agendar colheita")
            print("11. Listar agendamentos de colheita")
            print("12. Alocar recursos")
            print("13. Listar recursos alocados")
            print("14. Criar gráficos")
            print("15. Sincronizar com banco de dados")
            print("16. Listar operações pendentes")
            print("17. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                dados_simulados = gerar_dados_simulados()
                for dados in dados_simulados:
                    gerenciador.adicionar_dados(dados)
                print("Dados simulados inseridos com sucesso.")
            elif opcao == '2':
                ano = validar_ano(int(input("Digite o ano dos dados que deseja alterar: ")))
                campo = input("Digite o campo que deseja alterar (quantidade_colhida, temperatura_media, precipitacao, indice_maturidade, ph, nutrientes): ")
                valor = input_float("Digite o novo valor: ")
                gerenciador.alterar_dados(ano, campo, valor)
                print("Dados alterados com sucesso.")
            elif opcao == '3':
                ano = validar_ano(int(input("Ano: ")))
                quantidade_colhida = input_float("Quantidade colhida: ")
                temperatura_media = input_float("Temperatura média: ")
                precipitacao = input_float("Precipitação: ")
                indice_maturidade = input_float("Índice de maturidade: ")
                ph = input_float("pH do solo: ")
                nutrientes = input_float("Quantidade de nutrientes: ")
                
                novos_dados = DadosCompletos(
                    colheita=Colheita(ano=ano, quantidade_colhida=quantidade_colhida),
                    clima=Clima(ano=ano, temperatura_media=temperatura_media, precipitacao=precipitacao),
                    maturidade=MaturidadeCana(ano=ano, indice_maturidade=indice_maturidade),
                    solo=CondicoesSolo(ano=ano, ph=ph, nutrientes=nutrientes)
                )
                gerenciador.adicionar_dados(novos_dados)
                print("Novos dados incluídos com sucesso.")
            elif opcao == '4':
                ano = validar_ano(int(input("Digite o ano dos dados que deseja excluir: ")))
                gerenciador.excluir_dados(ano)
                print("Dados excluídos com sucesso.")
            elif opcao == '5':
                confirmacao = input("ATENÇÃO: Isso irá excluir TODOS os dados. Digite 'CONFIRMAR' para prosseguir: ")
                if confirmacao == 'CONFIRMAR':
                    gerenciador.excluir_todos_dados()
                    print("Todos os dados foram excluídos.")
                else:
                    print("Operação cancelada.")
            elif opcao == '6':
                    gerenciador.carregar_dados_json()
            elif opcao == '7':
                df = carregar_dados_db(conn, logging)
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        dados = DadosCompletos(
                            colheita=Colheita(ano=row['ano'], quantidade_colhida=row['quantidade_colhida']),
                            clima=Clima(ano=row['ano'], temperatura_media=row['temperatura_media'], precipitacao=row['precipitacao']),
                            maturidade=MaturidadeCana(ano=row['ano'], indice_maturidade=row['indice_maturidade']),
                            solo=CondicoesSolo(ano=row['ano'], ph=row['ph'], nutrientes=row['nutrientes'])
                        )
                        gerenciador.adicionar_dados(dados)
                    print("Dados carregados do banco com sucesso.")
                else:
                    print("Não foi possível carregar dados do banco.")
            elif opcao == '8':
                df = carregar_dados_db(conn, logging)
                if not df.empty:
                    X, y = preparar_dados(df, logging)
                    modelo = treinar_modelo(X, y, logging)

                    print("Modelo treinado com sucesso!")
                else:
                    print("Não há dados suficientes para treinar o modelo.")
            elif opcao == '9':
                if modelo is None:
                    print("Primeiro treine o modelo usando a opção 8.")
                else:
                    fazer_previsao(modelo, logging)
            elif opcao == '10':
                plantacao_id = int(input("ID da plantação: "))
                data_colheita = datetime.strptime(input("Data da colheita (YYYY-MM-DD): "), "%Y-%m-%d")
                gerenciador.agendar_colheita(plantacao_id, data_colheita)
                print("Colheita agendada com sucesso.")
            elif opcao == '11':
                agendamentos = gerenciador.listar_agendamentos()
                if agendamentos:
                    print("\nAgendamentos de Colheita:")
                    for data, plantacao_id in agendamentos:
                        print(f"Plantação ID: {plantacao_id}, Data Colheita: {data.strftime('%Y-%m-%d')}")
                else:
                    print("Não há agendamentos de colheita.")
            elif opcao == '12':
                gerenciador.alocar_recurso(conn)
                print("Recurso alocado com sucesso.")
            elif opcao == '13':
                recursos = gerenciador.recursos_alocados
                if recursos:
                    print("\nRecursos Alocados:")
                    for recurso in recursos:
                        print(recurso)
                else:
                    print("Não há recursos alocados.")
            elif opcao == '14':
                df = carregar_dados_db(conn, logging)
                criar_graficos(df, logging)
            elif opcao == '15':
                gerenciador.sincronizar_com_banco(conn)
                print("Dados sincronizados com o banco de dados.")
           
            elif opcao == '16':
                print("\nOperações Pendentes:")
                for index, operacao in enumerate(gerenciador.operacoes_pendentes):
                    print(f"Índice: {index + 1} - Operação: {operacao}")

            elif opcao == '17':
                print("Saindo do programa...")
                break

            else:
                print("Opção inválida. Por favor, tente novamente.")

    except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            print(f"Ocorreu um erro: {e}")

    finally:
            if conn:
                fechar_conexao(conn)
            logging.info("Conexão com o banco de dados fechada")


# Executar o menu principal
if __name__ == "__main__":
    menu_principal()
