
from datetime import datetime

# Funções auxiliares
def input_float(prompt):
    """
    Solicita entrada do usuário e converte para float.

    Args:
    prompt (str): Mensagem a ser exibida ao usuário.

    Returns:
    float: Valor inserido pelo usuário.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Por favor, insira um número válido.")

            # Funções de visualização


def validar_ano(ano):
    """
    Valida o ano inserido.

    Args:
    ano (int): Ano a ser validado.

    Returns:
    int: Ano validado.

    Raises:
    ValueError: Se o ano for inválido.
    """
    atual = datetime.now().year
    if ano < 1900 or ano > atual + 1:
        raise ValueError(f"Ano deve estar entre 1900 e {atual + 1}")
    return ano