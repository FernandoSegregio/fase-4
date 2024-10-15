
<img src="../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=30% height=30%>

# Além do Python - Fase 2 - FIAP

## Nome do Grupo
TerraFusion Tech


#### Nomes dos integrantes do grupo
- <a href="https://www.linkedin.com/in/ana-kolodji-94ba66324/">Ana Kolodi</a>
- <a href="https://www.linkedin.com/in/fernando-segregio/">Fernando Miranda Segregio</a>
- <a href="https://www.linkedin.com/in/tatiana-vieira-lopes-dos-santos-368396b3">Tatiana Lopes</a>



## Sumário

[1. Introdução](#c1)

[2. Visão Geral do Projeto](#c2)

[3. Desenvolvimento do Projeto](#c3)

<br>
<br>

# <a name="c1"></a>1. Introdução

## 1.1. Escopo do Projeto

### 1.1.1. Contexto da Inteligência Artificial

O agronegócio é um dos setores mais importantes e complexos do Brasil, representando uma grande parcela da economia nacional. Ele envolve cadeias produtivas interconectadas, desde a produção agrícola e pecuária até o processamento, distribuição e comercialização de alimentos e produtos derivados. Dada essa complexidade, identificar pontos de melhoria e dores específicas dentro desse segmento é essencial para aumentar a eficiência, a sustentabilidade e a lucratividade das operações.


### 1.1.2. Descrição da Solução Desenvolvida

O Brasil é líder mundial na produção de cana-de-açúcar, mas enfrenta desafios significativos relacionados às perdas durante a colheita. Essas perdas podem chegar a 15% quando a colheita é realizada mecanicamente, representando um prejuízo considerável para os produtores e para a economia como um todo.

Nossa solução integra:
- Gestão de dados históricos de colheita
- Análise de fatores climáticos e do solo
- Previsão de colheita utilizando machine learning
- Agendamento e alocação de recursos para a colheita

# <a name="c2"></a>2. Visão Geral do Projeto

## 2.1. Objetivos do Projeto

O objetivo deste projeto é criar uma solução tecnológica que auxilie a tomada de decisão em um dos processos críticos dentro do agronegócio, com ênfase em:

Gestão de Recursos Agrícolas: Otimização da alocação de maquinário, recursos humanos e insumos agrícolas para as atividades de plantio e colheita.
Monitoramento das Condições Climáticas e do Solo: Armazenamento e análise de dados climáticos e do solo para prever a melhor época de colheita e otimizar o uso de fertilizantes e irrigação.
Análise da Produção e da Colheita: Analisar a quantidade colhida ao longo dos anos para identificar tendências e prever safras futuras.

## 2.2. Público-Alvo

1. Produtores Rurais e Gerentes de Propriedades Agrícolas
Objetivo: Utilizar o sistema para gerenciar as operações de colheita de cana-de-açúcar em suas propriedades.
Necessidade: Aumentar a eficiência, prever a melhor época para colher e reduzir perdas financeiras.
2. Engenheiros Agrônomos e Consultores Agrícolas
Objetivo: Analisar dados históricos, climáticos e do solo para fornecer recomendações otimizadas sobre a colheita e o manejo agrícola.
Necessidade: Utilizar ferramentas tecnológicas para tomar decisões informadas e baseadas em dados.
3. Empresas e Cooperativas do Agronegócio
Objetivo: Aumentar a produtividade e lucratividade por meio da automação e previsões precisas.
Necessidade: Gerenciar grandes áreas de produção com o uso otimizado de recursos e pessoal.

## 2.3. Metodologia

A metodologia utilizada para o desenvolvimento do projeto foi baseada em CRISP-DM (Cross Industry Standard Process for Data Mining), que é amplamente utilizada em projetos de mineração de dados e machine learning. As etapas seguidas foram:

Compreensão do Negócio: Estudamos o setor do agronegócio, focando nos desafios da colheita de cana-de-açúcar. Isso incluiu o levantamento de dados históricos de colheita e análise de fatores como clima e maturidade da cana.

Compreensão dos Dados: Coletamos e analisamos os dados, incluindo informações climáticas e de solo. Exploramos esses dados para identificar padrões e outliers que pudessem afetar a colheita.

Modelagem: Desenvolvemos modelos de machine learning para prever o momento ideal de colheita. Utilizamos algoritmos como Random Forest e Regressão Linear, considerando variáveis climáticas e condições do solo.

Avaliação: Avaliamos o desempenho dos modelos utilizando métricas como acurácia e erro médio absoluto (MAE), garantindo que o modelo fosse capaz de prever com precisão o melhor momento para a colheita.

Implementação: Integramos o modelo preditivo ao sistema de gestão, permitindo a automação do agendamento da colheita e a otimização de recursos.

2.3. Metodologia
A metodologia seguida no projeto foi baseada em um pipeline de machine learning, utilizando dados históricos e técnicas de aprendizado supervisionado. As principais etapas foram:

Coleta e Preparação de Dados: Utilizamos o Pandas para manipulação e análise dos dados. O dataset continha variáveis como temperatura média, precipitação, índice de maturidade da cana-de-açúcar, pH do solo e quantidade de nutrientes, além da variável alvo quantidade colhida.

Selecionamos features relevantes (temperatura, precipitação, índice de maturidade, pH e nutrientes).
Definir a variável alvo y como a quantidade colhida.
Treinamento do Modelo: O modelo escolhido foi o Random Forest Regressor, uma técnica robusta para problemas de regressão e que lida bem com dados de alta dimensionalidade e não linearidades.

Divisão dos dados: Usamos a função train_test_split da biblioteca Scikit-learn para dividir os dados em conjuntos de treino e teste, reservando 20% dos dados para o conjunto de teste.

Treinamento: A função treinar_modelo(X, y, logging) realizou o treinamento do modelo com 100 estimadores, utilizando a métrica de erro quadrático médio (RMSE) para avaliar a performance.

Avaliação: O RMSE foi calculado utilizando a função root_mean_squared_error, permitindo medir a precisão das previsões em toneladas de colheita.
Predição: Após o treinamento, a função fazer_previsao(modelo, logging) permitiu que os usuários fizessem previsões fornecendo novos dados sobre temperatura, precipitação, índice de maturidade, pH e nutrientes.

Os dados inseridos foram convertidos em um DataFrame do Pandas, com a estrutura esperada pelo modelo.
A previsão foi feita utilizando o modelo treinado, retornando a estimativa da quantidade colhida em toneladas.
Ferramentas Utilizadas:


# <a name="c3"></a>3. Desenvolvimento do Projeto

## 3.1. Tecnologias Utilizadas e funcionalidades
* Python como linguagem principal de programação.
* Pandas para manipulação e análise de dados.
* Scikit-learn para as funções de machine learning, como RandomForestRegressor, train_test_split, e root_mean_squared_error.
* Funções auxiliares customizadas como input_float para coleta de dados interativa.
* Logging para registrar informações relevantes, como o RMSE após o treinamento e os resultados das previsões.
* Oracledb SQLAlchemy conexão e manipulação de banco
* Logging para esvrever logs em arquivo txt
* Matplotlib para geração de Grafocps 

1. Inserção e Manipulação de Dados
Inserir dados simulados: Gerar dados simulados automaticamente para testes.
Alterar dados: Modificar valores específicos nos dados já existentes.
Incluir novos dados: Adicionar dados manuais de colheita, clima, maturidade e solo.
Excluir dados: Remover dados de um ano específico ou excluir todos os dados armazenados.
2. Carga de Dados
Carregar dados de arquivo JSON: Importar dados a partir de um arquivo JSON.
Carregar dados do banco de dados: Sincronizar e carregar dados diretamente do banco de dados.
3. Machine Learning
Treinar modelo de previsão: Utiliza aprendizado de máquina para treinar um modelo de previsão da colheita.
Fazer previsão de colheita: Utiliza o modelo treinado para prever a colheita de cana-de-açúcar com base nos dados inseridos.
4. Agendamento de Colheitas
Agendar colheita: Planejar uma colheita futura com base em uma data definida pelo usuário.
Listar agendamentos de colheita: Exibir todas as colheitas agendadas.
5. Alocação de Recursos
Alocar recursos: Automatiza a alocação de recursos para o processo de colheita.
Listar recursos alocados: Exibe os recursos que foram alocados.
6. Geração de Gráficos
Criar gráficos: Gerar gráficos para visualização dos dados, facilitando a análise das condições da colheita.
7. Sincronização e Operações Pendentes
Sincronizar com banco de dados: Sincroniza os dados manipulados com o banco de dados.
Listar operações pendentes: Exibe operações que ainda não foram finalizadas ou sincronizadas.

## 3.1.1 Todas Funcionalidades

### Atividades do Usuário na Aplicação

1. **Inserir Dados Simulados**:
   - O usuário pode gerar e inserir dados simulados na aplicação.

2. **Alterar Dados**:
   - O usuário pode modificar os dados existentes, alterando campos específicos de um ano determinado.

3. **Incluir Novos Dados**:
   - O usuário pode adicionar novos dados de colheita, clima, maturidade e condições do solo para um ano específico.

4. **Excluir específicos**:
   - O usuário pode excluir dados específicos de um ano escolhido.

5. **Excluir todos os dados**:
   - O usuário pode excluir todos os dados, mediante confirmação.

6. **Carregar Dados de Arquivo JSON**:
   - O usuário pode carregar dados de um arquivo JSON que contém informações de anos anteriores.

7. **Carregar Dados do Banco**:
   - O usuário pode carregar dados existentes do banco de dados para visualizar ou manipular.

8. **Treinar Modelo de Previsão**:
   - O usuário pode treinar um modelo de previsão, desde que haja dados suficientes carregados do banco de dados.

9. **Fazer Previsão de Colheita**:
   - O usuário pode fazer previsões de colheita utilizando um modelo previamente treinado.

10. **Agendar Colheita**:
   - O usuário pode agendar uma colheita para uma plantação específica em uma data escolhida.

11. **Listar Agendamentos de Colheita**:
    - O usuário pode visualizar todos os agendamentos de colheita existentes.

12. **Alocar Recursos**:
    - O usuário pode alocar recursos necessários para a colheita.

13. **Listar Recursos Alocados**:
    - O usuário pode visualizar todos os recursos que foram alocados.

14. **Criar Gráficos**:
    - O usuário pode gerar gráficos com base nos dados disponíveis no banco de dados.

15. **Sincronizar com Banco de Dados**:
    - O usuário pode sincronizar os dados manipulados na aplicação com o banco de dados.

16. **Listar Operações Pendentes**:
    - O usuário pode visualizar as operações pendentes que estão agendadas na aplicação.

### 3.1.2 Considerações

- Para realizar **Treinar Modelo de Previsão** e **Criar Gráficos**, o usuário precisa garantir que existem dados no banco de dados, que podem ser inseridos através das atividades **Inserir Dados Simulados** ou **Carregar Dados de Arquivo JSON**.
- As operações de inserção de dados e carregamento de arquivos são essenciais para alimentar a aplicação com informações necessárias para as funcionalidades de análise e previsão, sempre que realizar o carregamento de algum item para ser inserido no banco é nescessário executar a funcionalidade **15 - Sincronizar com o Banco de dados**.


Dicas: Experimente, inserir dados simulados (1), os dados serão carregados a partir de uma lista carregada previamente, ou experimente, usar a função que carrega dados de um JSON (6) com os valores das colheitas e produção de anos anteriores. Após selecionar de onde você quer inserir dados, use a função para sincronizar dados com o banco (15), após garantir a existência de dados no banco, treine o modelo, crie gráficos e muito mais!


