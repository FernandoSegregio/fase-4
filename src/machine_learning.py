import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from func_auxiliar import input_float

# Funções de machine learning

def preparar_dados(df, logging):
   
    print(df.head())  # Mostre as primeiras linhas do DataFrame

    """
    Prepara os dados para o modelo de machine learning.

    Args:
    df (pandas.DataFrame): DataFrame contendo os dados.

    Returns:
    tuple: Features (X) e target (y) para o modelo.
    """
    X = df[['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes']]
    y = df['quantidade_colhida']
    return X, y

def treinar_modelo(X, y, logging):
    """
    Treina o modelo de machine learning.

    Args:
    X: Features para treinamento.
    y: Target para treinamento.

    Returns:
    RandomForestRegressor: Modelo treinado.
    """
    # Dividir os dados em conjunto de treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Criar e treinar o modelo
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    # Fazer previsões
    previsoes = modelo.predict(X_test)
    
    # Calcular o RMSE usando a função root_mean_squared_error
    erro_rmse = root_mean_squared_error(y_test, previsoes)
    logging.info(f'Modelo treinado. Erro quadrático médio (RMSE): {erro_rmse:.2f} toneladas')
    
    return modelo

def fazer_previsao(modelo, logging):
    """
    Faz uma previsão usando o modelo treinado.

    Args:
    modelo: Modelo de machine learning treinado.
    gerenciador: Instância de GerenciadorDados.
    """
    print("\nInsira os dados para a previsão:")
    temperatura = input_float("Temperatura média: ")
    precipitacao = input_float("Precipitação: ")
    indice_maturidade = input_float("Índice de maturidade: ")
    ph = input_float("pH do solo: ")
    nutrientes = input_float("Quantidade de nutrientes: ")

    dados_previsao = pd.DataFrame([[temperatura, precipitacao, indice_maturidade, ph, nutrientes]], 
                                  columns=['temperatura_media', 'precipitacao', 'indice_maturidade', 'ph', 'nutrientes'])
    
    previsao = modelo.predict(dados_previsao)
    print(f"\nPrevisão de colheita: {previsao[0]:.2f} toneladas")
    logging.info(f"Previsão realizada: {previsao[0]:.2f} toneladas")