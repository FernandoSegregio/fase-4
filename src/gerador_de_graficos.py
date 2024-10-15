import matplotlib.pyplot as plt
from datetime import datetime

def criar_graficos(df, logging):
    """
    Cria gráficos baseados nos dados do gerenciador.

    Args:
    df: DataFrame com os dados.
    logging: Logger para registrar informações.
    """
    print(df)
    anos = list(df['ano'])
    quantidades = df['quantidade_colhida']
    temperaturas = df['temperatura_media']
    precipitacoes = df['precipitacao']

    # Log dos dados
    logging.info(f"Ano: {anos}, Quantidades: {quantidades}, Temperaturas: {temperaturas}, Precipitações: {precipitacoes}")

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Formato: AAAA-MM-DD_HH-MM-SS

    # Criar o nome do arquivo com a data e a hora
    filename_colhida = f'src/graficos/quantidade_colhida_{timestamp}.png' 
    filename_clima = f'src/graficos/clima_{timestamp}.png' 

    # Gráfico da Quantidade Colhida
    plt.figure(figsize=(10, 6))
    plt.plot(anos, quantidades, marker='o', linestyle='-', alpha=0.7)
    plt.title('Quantidade Colhida ao Longo dos Anos')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade Colhida')
    plt.grid(True)
    plt.savefig(filename_colhida)
    plt.close()  

    # Gráfico de Temperatura e Precipitação
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    ax1.bar(anos, temperaturas, color='r', alpha=0.5, label='Temperatura Média')
    ax2.bar(anos, precipitacoes, color='b', alpha=0.5, label='Precipitação')
    ax1.set_xlabel('Ano')
    ax1.set_ylabel('Temperatura Média (°C)', color='r')
    ax2.set_ylabel('Precipitação (mm)', color='b')
    plt.title('Temperatura Média e Precipitação por Ano')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.savefig(filename_clima)
    plt.close()  # Fecha o gráfico atual para liberar memória

    logging.info("Gráficos criados e salvos como %s e %s", filename_clima, filename_colhida)
    print(f"Gráficos criados e salvos como {filename_clima} e {filename_colhida}")
