"""
Script de prueba para el sistema de auditoría del asistente.
"""
import sys
import os
import time
import random
from datetime import datetime, timedelta

# Añadir el directorio actual al path para importar el módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from asistente_avanzado import Auditoria, TipoEvento

def test_auditoria_basica():
    """Prueba básica del sistema de auditoría."""
    print("\n=== Iniciando prueba básica del sistema de auditoría ===")
    
    # Obtener instancia del auditor
    auditoria = Auditoria()
    
    # Registrar algunos eventos de prueba
    print("\nRegistrando eventos de prueba...")
    
    # Evento de inicio de sesión
    auditoria.registrar_evento(
        tipo=TipoEvento.ACCION_USUARIO,
        accion="Inicio de sesión",
        detalles={"usuario": "usuario_prueba", "origen": "formulario_web"},
        resultado="éxito"
    )
    
    # Evento de comando de voz
    auditoria.registrar_evento(
        tipo=TipoEvento.COMANDO_VOZ,
        accion="Comando de voz procesado",
        detalles={"comando": "abrir navegador", "confianza": 0.95},
        resultado="navegador_abierto"
    )
    
    # Evento de error
    try:
        # Simular un error
        raise ValueError("Error de prueba")
    except Exception as e:
        auditoria.registrar_evento(
            tipo=TipoEvento.ERROR,
            accion="Error en procesamiento",
            detalles={"tipo": type(e).__name__, "mensaje": str(e)},
            resultado="error"
        )
    
    # Evento del sistema
    auditoria.registrar_evento(
        tipo=TipoEvento.SISTEMA,
        accion="Actualización de configuración",
        detalles={"parametro": "tema", "valor": "oscuro"},
        resultado="configuracion_actualizada"
    )
    
    print("✓ Eventos de prueba registrados correctamente")
    
    # Probar la obtención de eventos
    print("\nProbando obtención de eventos...")
    eventos = auditoria.obtener_eventos(limite=10)
    print(f"Se encontraron {len(eventos)} eventos en el registro")
    print("Últimos 3 eventos:")
    for evento in eventos[:3]:
        print(f"- [{evento['tipo']}] {evento['accion']} - {evento['timestamp']}")
    
    # Probar generación de informes
    print("\nProbando generación de informes...")
    
    # Generar informe en formato TXT
    informe_txt = auditoria.generar_informe(formato="txt")
    print(f"✓ Informe generado: {informe_txt}")
    
    # Generar informe en formato JSON
    informe_json = auditoria.generar_informe(formato="json")
    print(f"✓ Informe JSON generado: {informe_json}")
    
    # Generar informe en formato CSV
    informe_csv = auditoria.generar_informe(formato="csv")
    print(f"✓ Informe CSV generado: {informe_csv}")
    
    # Probar filtrado por fecha
    print("\nProbando filtrado por fecha...")
    fecha_ayer = datetime.now() - timedelta(days=1)
    eventos_recientes = auditoria.obtener_eventos(
        fecha_desde=fecha_ayer,
        limite=5
    )
    print(f"Eventos desde ayer: {len(eventos_recientes)}")
    
    # Probar limpieza de registros (con confirmación desactivada para la prueba)
    print("\nProbando limpieza de registros...")
    if auditoria.limpiar_eventos(confirmar=False):
        print("✓ Registros de auditoría limpiados correctamente")
        
        # Verificar que se hayan limpiado
        eventos_despues = auditoria.obtener_eventos()
        print(f"Eventos después de limpiar: {len(eventos_despues)}")
    else:
        print("✗ Error al limpiar los registros de auditoría")
    
    print("\n=== Prueba completada ===\n")

def test_rendimiento():
    """Prueba de rendimiento del sistema de auditoría."""
    print("\n=== Iniciando prueba de rendimiento ===")
    
    # Obtener instancia del auditor
    auditoria = Auditoria()
    
    # Número de eventos a generar
    num_eventos = 1000
    print(f"Generando {num_eventos} eventos de prueba...")
    
    # Tipos de eventos para la prueba
    tipos_eventos = [
        TipoEvento.ACCION_USUARIO,
        TipoEvento.COMANDO_VOZ,
        TipoEvento.SISTEMA,
        TipoEvento.ERROR
    ]
    
    # Medir tiempo de inicio
    inicio = time.time()
    
    # Generar eventos de prueba
    for i in range(num_eventos):
        tipo = random.choice(tipos_eventos)
        auditoria.registrar_evento(
            tipo=tipo,
            accion=f"Evento de prueba {i+1}",
            detalles={"iteracion": i, "aleatorio": random.random()},
            resultado="éxito" if random.random() > 0.1 else "error"
        )
    
    # Medir tiempo de fin
    fin = time.time()
    
    print(f"Tiempo total: {fin - inicio:.2f} segundos")
    print(f"Eventos por segundo: {num_eventos / (fin - inicio):.2f}")
    
    # Generar informe de rendimiento
    print("\nGenerando informe de rendimiento...")
    informe_rendimiento = auditoria.generar_informe(
        formato="txt",
        nombre="informe_rendimiento"
    )
    print(f"✓ Informe de rendimiento generado: {informe_rendimiento}")
    
    print("\n=== Prueba de rendimiento completada ===\n")

def test_seguridad():
    """Prueba de seguridad del sistema de auditoría."""
    print("\n=== Iniciando prueba de seguridad ===")
    
    # Obtener instancia del auditor
    auditoria = Auditoria()
    
    # Intentar acceder a atributos privados
    print("\nProbando acceso a atributos privados...")
    try:
        # Intentar acceder a atributos privados
        print(f"Intentando acceder a atributos privados...")
        # Esto debería fallar o no mostrar información sensible
        print(f"Atributos accesibles: {dir(auditoria)}")
        print("✗ Se pudo acceder a atributos internos")
    except Exception as e:
        print(f"✓ Acceso a atributos privados correctamente restringido: {e}")
    
    # Verificar que los logs no contengan información sensible
    print("\nVerificando protección de información sensible...")
    try:
        # Registrar evento con información sensible
        auditoria.registrar_evento(
            tipo=TipoEvento.SEGURIDAD,
            accion="Intento de acceso",
            detalles={"usuario": "admin", "contraseña": "no_deberia_aparecer"},
            resultado="error_autenticacion"
        )
        
        # Obtener el último evento
        eventos = auditoria.obtener_eventos(limite=1)
        if eventos and "no_deberia_aparecer" not in str(eventos[0]):
            print("✓ Información sensible correctamente ofuscada")
        else:
            print("✗ Se encontró información sensible en los logs")
    except Exception as e:
        print(f"Error en prueba de seguridad: {e}")
    
    print("\n=== Prueba de seguridad completada ===\n")

def menu_principal():
    """Muestra el menú principal de pruebas."""
    while True:
        print("\n=== Menú de Pruebas de Auditoría ===")
        print("1. Ejecutar prueba básica")
        print("2. Ejecutar prueba de rendimiento")
        print("3. Ejecutar prueba de seguridad")
        print("4. Ejecutar todas las pruebas")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            test_auditoria_basica()
        elif opcion == "2":
            test_rendimiento()
        elif opcion == "3":
            test_seguridad()
        elif opcion == "4":
            test_auditoria_basica()
            test_rendimiento()
            test_seguridad()
            print("\n✓ Todas las pruebas se han completado")
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción no válida. Por favor, intente de nuevo.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    print("=== Sistema de Pruebas de Auditoría ===")
    print("Este script prueba el funcionamiento del sistema de auditoría.\n")
    
    # Verificar que el módulo de auditoría esté disponible
    try:
        from asistente_avanzado import Auditoria, TipoEvento
        print("✓ Módulo de auditoría importado correctamente")
    except ImportError as e:
        print(f"✗ Error al importar el módulo de auditoría: {e}")
        print("Asegúrese de que el archivo 'asistente_avanzado.py' esté en el mismo directorio.")
        sys.exit(1)
    
    # Iniciar menú de pruebas
    menu_principal()
