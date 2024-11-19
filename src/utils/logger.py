import logging
from colorama import init, Fore, Style

# Inicializar colorama
init()

class ColoredFormatter(logging.Formatter):
    """Formateador personalizado para logs con colores"""
    def format(self, record):
        if record.levelno >= logging.ERROR:
            color = Fore.RED
        elif record.levelno >= logging.WARNING:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger():
    """Configura y retorna el logger"""
    logger = logging.getLogger('ConvertidorDirectorios')
    logger.setLevel(logging.INFO)
    
    # Evitar duplicados de handlers
    if logger.handlers:
        return logger
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = logging.FileHandler('convertidor.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    return logger
