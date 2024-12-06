# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
    <a href="https://www.fiap.com.br/">
        <img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%>
    </a>
</p>

<br>

# Nome do projeto
    FarmTech Solution

## Nome do grupo
    TerraFusion Tech - Sistema de Automação de Plantações

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/ana-kolodji-94ba66324/">Ana Kolodiji</a>
- <a href="https://www.linkedin.com/in/fernando-segregio/">Fernando Segregio</a>    
- <a href="https://www.linkedin.com/in/matheusconciani/">Matheus Conciani</a> 

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/lucas-gomes-moreira-15a8452a/">Lucas Gomes Moreira</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/profandregodoi/">André Godoi</a>


## 📜 Descrição

O Sistema de Automação de Plantações é um projeto desenvolvido pela equipe TerraFusion Tech. O sistema é projetado para realizar a gestão e automação de irrigação agrícola, monitorando sensores de umidade, temperatura, pH e nutrientes, e controlando bombas de água para irrigação automatizada.

### Funcionalidades Principais:

#### 🌡️ Monitoramento Inteligente
- Sensores de umidade, temperatura e pH em tempo real
- Dashboard interativo com métricas e gráficos
- Visualização histórica de dados
- Indicadores visuais de status (normal/crítico)

#### 🤖 Automação de Irrigação
- Controle automático baseado em umidade do solo
- Ativação quando umidade < 50%
- Desativação quando umidade ≥ 50%
- Comunicação via MQTT com ESP32

#### 📊 Análise Preditiva
- Modelo de machine learning para previsão de necessidade de irrigação
- Análise de dados históricos de clima
- Previsão de precipitação para 7 dias
- Sugestões automáticas de ação

#### 🌦️ Integração com APIs
- Previsão do tempo em tempo real
- Dados climatológicos históricos
- Tomada de decisão baseada em múltiplas fontes

O sistema utiliza análise avançada de dados e inteligência artificial para otimizar o uso de recursos hídricos, garantindo uma irrigação eficiente e sustentável das plantações.

## Dashboard da aplicação

![dashboard](image-3.png)




### Sistema Automação de Planaçãoes com leitor LCD

![LCD do sistema de irrigação](image-1.png)

### Grafico suavizado do Serial Plotter

![Grafico do Serial Plotter ](image-2.png)


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.

- <b>config</b>: Posicione aqui arquivos de configuração que são usados para definir parâmetros e ajustes do projeto.

- <b>document</b>: aqui estão todos os documentos do projeto que as atividades poderão pedir. Na subpasta "other", adicione documentos complementares e menos importantes.

- <b>src/scripts</b>: Posicione aqui scripts auxiliares para tarefas específicas do seu projeto. Exemplo: deploy, migrações de banco de dados, backups.

- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto ao longo das 7 fases.

- <b>PlatformIO</b>: Pasta com os arquivos da automação (wokwi + hivemq).

- <b>log</b>: Pasta para guardar os logs da aplicação em um arquivo txt.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).


## 🔧 Como executar o código

#### Pré-requisitos
Antes de começar, verifique se você tem os seguintes pré-requisitos instalados em sua máquina:

#### 1. IDEs
Visual Studio Code (ou qualquer outra IDE de sua preferência)
PyCharm (opcional, caso você prefira um ambiente específico para Python)
#### 2. Serviços
Python 3.6 ou superior: O projeto foi desenvolvido e testado com Python 3.8.
Oracle Database: Para conectar-se ao banco de dados, você deve ter acesso a uma instância do Oracle.
#### 3. Bibliotecas
Bibliotecas Python: As bibliotecas necessárias estão listadas no arquivo requirements.txt. Abaixo estão algumas das principais bibliotecas utilizadas:

matplotlib: Para visualização de dados em forma de gráficos
pandas: Para manipulação de dados
SQLAlchemy: conexão com banco de dados
oracledb: Para conexão com o banco de dados Oracle
logging: Para Logs da aplicação

Confira todas as bibliotecas utilizadas estão no arquivo requirements

#### 4. Versões
As bibliotecas utilizadas estão no arquivo requirements

*requirements.txt*


#### Passos para configurar o ambiente:

1 - Com o código abaixo, crie um arquivo .env na raiz do seu projeto e preencha com os dados das suas variáveis de ambiente para conexão com o banco de dados:

```
echo -e "DB_USER=\nDB_PASSWORD=\nDB_DSN=" > .env
```
</br>

#### Antes de iniciar a aplicação em Python, vamos inicar a aplicação em so Simulador, nosso sistema é todo automatico, o sistema de irrigação envia via fila do hivemq os dados para a aplicação em Python que consome essses dados.

### Iniciando a automação ###

1. Setup da Maquina

#### Para macOS:
```
setup-mac
```

#### Para Linux:
```
setup-linux
```

#### Para Windows:
```
setup-windows:
```

2. Faça o setup do banco de dados
```
make setup_db
```

3. Iniciar a aplicação

```
make run
```
3. Executar o Projeto

Após compilar, você pode carregar e executar o código clicando no botão "Play" do diagram.json que está na pasta PlatformIO

<br />

Ou abra o link no navegador e aperte play

https://wokwi.com/projects/416547430655986689



Dicas:
- 1 - Variáveis de Ambiente: Lembre-se de preencher o arquivo **.env** com os valores corretos para **DB_USER**, **DB_PASSWORD** e **DB_DSN** antes de rodar o aplicativo.<br />
- 2 - Antes de **ativar o ambiente** verifique qual é seu **sistema operacional** e escolha o comando correto.

Projeto Wokwi:

https://wokwi.com/projects/416547430655986689

## 🗃 Histórico de lançamentos

* 0.1.0 - 14/10/2024
 
* 0.1.1 - 13/11/2024
  
* 0.2.0 - 06/12/2024
    
<!--* 0.2.0 - XX/XX/2024
    * 
* 0.1.0 - XX/XX/2024 -->


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>


