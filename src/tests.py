import unittest

from gerenciador import GerenciadorDados
from gerenciador import DadosCompletos
from gerenciador import Colheita
from gerenciador import MaturidadeCana
from gerenciador import Clima
from gerenciador import CondicoesSolo

# Testes unitários

class TestGerenciadorDados(unittest.TestCase):
    def setUp(self):
        self.gerenciador = GerenciadorDados()

    def test_adicionar_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.assertIn(2024, self.gerenciador.dados_por_ano)
        self.assertEqual(self.gerenciador.dados_por_ano[2024], dados)

    def test_alterar_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.gerenciador.alterar_dados(2024, 'quantidade_colhida', 1800)
        self.assertEqual(self.gerenciador.dados_por_ano[2024].colheita.quantidade_colhida, 1800)

    def test_excluir_dados(self):
        dados = DadosCompletos(
            colheita=Colheita(ano=2024, quantidade_colhida=1700),
            clima=Clima(ano=2024, temperatura_media=26.0, precipitacao=1180),
            maturidade=MaturidadeCana(ano=2024, indice_maturidade=0.87),
            solo=CondicoesSolo(ano=2024, ph=6.5, nutrientes=0.77)
        )
        self.gerenciador.adicionar_dados(dados)
        self.gerenciador.excluir_dados(2024)
        self.assertNotIn(2024, self.gerenciador.dados_por_ano)

    def test_agendar_colheita(self):
        self.gerenciador.agendar_colheita(1, datetime(2024, 5, 1))
        agendamentos = self.gerenciador.listar_agendamentos()
        self.assertEqual(len(agendamentos), 1)
        self.assertEqual(agendamentos[0][1], 1)  # plantacao_id
        self.assertEqual(agendamentos[0][0], datetime(2024, 5, 1))  # data_colheita

    def test_alocar_recurso(self):
        self.gerenciador.alocar_recurso("Trator")
        self.assertIn("Trator", self.gerenciador.recursos_alocados)