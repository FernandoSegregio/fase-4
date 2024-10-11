import logging
import os
from logging.handlers import RotatingFileHandler

def configurar_logging():
   
    # Define o diretório onde o log será salvo
    diretorio_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_logs')
    os.makedirs(diretorio_log, exist_ok=True)  # Cria o diretório se não existir

    caminho_log = os.path.join(diretorio_log, 'app.txt')

    handler = RotatingFileHandler(
        caminho_log,
        maxBytes=5*1024*1024,    # 5 MB por arquivo de log
        backupCount=5,           # Mantém até 5 arquivos de backup
        encoding='utf-8'
    )

    # Configuração básica do logging
    logging.basicConfig(
        level=logging.INFO,  
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',  
        handlers=[
            handler,           
            logging.StreamHandler()  
        ]
    )

    # Cria e retorna um logger para o módulo
    logger = logging.getLogger(__name__)
    return logger