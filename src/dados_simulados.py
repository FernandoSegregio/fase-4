from gerenciador import GerenciadorDados
from gerenciador import DadosCompletos
from gerenciador import Colheita
from gerenciador import MaturidadeCana
from gerenciador import Clima
from gerenciador import CondicoesSolo

# Funções de manipulação de dados
def gerar_dados_simulados():
    """
    Gera dados simulados para teste.

    Returns:
    List[DadosCompletos]: Lista de objetos DadosCompletos com dados simulados.
    """
    return [
        DadosCompletos(
            colheita=Colheita(ano=2021, quantidade_colhida=1500),
            clima=Clima(ano=2021, temperatura_media=25.3, precipitacao=1200),
            maturidade=MaturidadeCana(ano=2021, indice_maturidade=0.85),
            solo=CondicoesSolo(ano=2021, ph=6.5, nutrientes=0.75)
        ),
        DadosCompletos(
            colheita=Colheita(ano=2022, quantidade_colhida=1600),
            clima=Clima(ano=2022, temperatura_media=26.1, precipitacao=1100),
            maturidade=MaturidadeCana(ano=2022, indice_maturidade=0.88),
            solo=CondicoesSolo(ano=2022, ph=6.4, nutrientes=0.78)
        ),
        DadosCompletos(
            colheita=Colheita(ano=2023, quantidade_colhida=1550),
            clima=Clima(ano=2023, temperatura_media=25.8, precipitacao=1150),
            maturidade=MaturidadeCana(ano=2023, indice_maturidade=0.86),
            
                        solo=CondicoesSolo(ano=2023, ph=6.6, nutrientes=0.76)
        )
    ]