from loguru import logger
import os
from pathlib import Path

# Verificar si ya existe una configuración previa (evitar duplicación)
if not logger._core.handlers:
    # Obtener la ruta base del proyecto
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOG_DIR = BASE_DIR / 'logs'
    
    # Asegurar que el directorio de logs exista
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Configurar logger
    logger.add(
        LOG_DIR / 'dj5_helpdesk_{time:YYYY-MM-DD}.log',
        rotation='00:00',
        retention='60 days',
        level='DEBUG',
        encoding='utf-8',
        format='{time:YY-MM-DD HH:mm} | {level} | {message}',
    )

# Exportamos logger ya configurado
__all__ = ['logger']