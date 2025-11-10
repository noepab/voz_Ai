"""
Configuración global de pytest para el proyecto.

Este archivo contiene configuraciones y fixtures que estarán disponibles
para todas las pruebas del proyecto.
"""
import os
import sys
from pathlib import Path

import pytest

# Añadir el directorio raíz al path de Python
sys.path.insert(0, str(Path(__file__).parent))

# Configuración de logging para pruebas
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixtures comunes

@pytest.fixture(scope="session")
def test_data_dir():
    """Retorna la ruta al directorio de datos de prueba."""
    return Path(__file__).parent / "test_data"

@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch):
    """Configura el entorno de prueba."""
    # Configurar variables de entorno para pruebas
    monkeypatch.setenv("ENVIRONMENT", "TEST")
    
    # Cambiar el directorio de trabajo al directorio del proyecto
    monkeypatch.chdir(Path(__file__).parent)

# Configuración de cobertura
@pytest.fixture(autouse=True)
def check_test_coverage():
    """Verifica la cobertura de código después de las pruebas."""
    # Configuración inicial
    import coverage
    cov = coverage.Coverage()
    cov.start()
    
    yield  # Aquí se ejecutan las pruebas
    
    # Generar reporte de cobertura
    cov.stop()
    cov.save()
    cov.report()
    
    # Guardar reporte HTML
    cov.html_report(directory='htmlcov')
    
    # Fallar si la cobertura es menor al 80%
    cov_fail_under = 80
    cov_percent = cov.report()
    if cov_percent < cov_fail_under:
        logger.warning(f"La cobertura de código es {cov_percent:.2f}%, que es menor que el {cov_fail_under}% requerido.")
        # Descomenta la siguiente línea para hacer que falle la prueba si no se cumple la cobertura
        # pytest.fail(f"La cobertura de código es insuficiente: {cov_percent:.2f}% < {cov_fail_under}%")
