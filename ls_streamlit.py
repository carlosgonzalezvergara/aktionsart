# -*- coding: utf-8 -*-
"""
Wrapper de Streamlit para ls.py original
MANTIENE 100% LA LÓGICA ORIGINAL SIN MODIFICACIONES
"""

import streamlit as st
import sys
import os
import importlib
from typing import Optional, Any, Callable
from io import StringIO
import contextlib

# ==================== MONKEY PATCHING PARA CAPTURAR I/O ====================

class NecesitaInputException(Exception):
    """Excepción especial cuando se necesita input del usuario"""
    def __init__(self, prompt, tipo, key):
        self.prompt = prompt
        self.tipo = tipo
        self.key = key
        super().__init__(f"Necesita input: {key}")

class StreamlitInputCapture:
    """Captura las llamadas a peticion() e input_si_no() del código original"""
    
    def __init__(self):
        self.contador_preguntas = 0
        self.respuestas = {}
        
    def peticion(self, prompt: str) -> str:
        """Reemplazo de peticion() que usa Streamlit"""
        # Generar key único basado en el prompt y el contador
        key = f"p_{self.contador_preguntas}_{hash(prompt) % 10000}"
        self.contador_preguntas += 1
        
        # Verificar si ya tenemos respuesta guardada
        if key in st.session_state.get('ls_respuestas', {}):
            return st.session_state.ls_respuestas[key]
        
        # Si no tenemos respuesta, lanzar excepción para pausar ejecución
        raise NecesitaInputException(prompt, 'texto', key)
    
    def input_si_no(self, prompt: str) -> bool:
        """Reemplazo de input_si_no() que usa Streamlit"""
        key = f"p_{self.contador_preguntas}_{hash(prompt) % 10000}"
        self.contador_preguntas += 1
        
        # Verificar si ya tenemos respuesta guardada
        if key in st.session_state.get('ls_respuestas', {}):
            respuesta = st.session_state.ls_respuestas[key]
            # Normalizar respuesta
            if isinstance(respuesta, str):
                return respuesta.lower() in ['sí', 'si', 's', 'yes', 'true']
            return bool(respuesta)
        
        # Si no tenemos respuesta, lanzar excepción para pausar ejecución
        raise NecesitaInputException(prompt, 'si_no', key)


# ==================== SISTEMA DE EJECUCIÓN INCREMENTAL ====================

def ejecutar_ls_original():
    """Ejecuta el código original de ls.py con interceptación de I/O"""
    
    # Inicializar respuestas si no existen
    if 'ls_respuestas' not in st.session_state:
        st.session_state.ls_respuestas = {}
    
    # Preparar el capture
    if 'ls_capture' not in st.session_state:
        st.session_state.ls_capture = StreamlitInputCapture()
    
    # IMPORTANTE: Resetear el contador antes de cada ejecución
    st.session_state.ls_capture.contador_preguntas = 0
    capture = st.session_state.ls_capture
    
    # Importar y monkey-patch el módulo original
    sys.path.insert(0, '/mnt/user-data/uploads')
    
    # Capturar stdout para obtener el resultado final
    output_buffer = StringIO()
    
    try:
        # CRITICAL: Recargar el módulo para asegurar estado limpio
        import importlib
        if 'ls' in sys.modules:
            import ls
            importlib.reload(ls)
        else:
            import ls
        
        # Reemplazar las funciones de entrada DESPUÉS de recargar
        ls.peticion = capture.peticion
        ls.input_si_no = capture.input_si_no
        
        # Preparar argumentos iniciales desde session_state
        if hasattr(st.session_state, 'ls_akt_inicial'):
            sys.argv = ['ls.py', 
                       st.session_state.ls_akt_inicial, 
                       st.session_state.ls_oracion_inicial,
                       'dinamico' if st.session_state.get('ls_dinamico_inicial', False) else 'no_dinamico']
        
        # Silenciar algunos prints para evitar ruido
        import io
        
        # Ejecutar el código original capturando stdout
        with contextlib.redirect_stdout(output_buffer):
            # Crear un nuevo contexto de ejecución
            resultado = ls.main()
        
        # Si llegamos aquí, la ejecución terminó
        st.session_state.ls_output = output_buffer.getvalue()
        return True, None
            
    except NecesitaInputException as e:
        # El código necesita input - retornar la pregunta
        return False, e
            
    except Exception as e:
        st.error(f"Error durante la ejecución: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False, None


# ==================== INTERFAZ DE STREAMLIT ====================

def inicializar_estado_ls():
    """Inicializa el estado del wrapper"""
    defaults = {
        'ls_paso': 'inicio',
        'ls_capture': None,
        'ls_akt_inicial': None,
        'ls_oracion_inicial': '',
        'ls_dinamico_inicial': False,
        'ls_output': '',
        'ls_respuestas': {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Inicializar capture si no existe
    if st.session_state.ls_capture is None:
        st.session_state.ls_capture = StreamlitInputCapture()


def paso_inicio_ls():
    """Paso inicial - configuración antes de ejecutar ls.py"""
    st.markdown("## 📐 Generador de Estructuras Lógicas")
    st.markdown("### Wrapper del código original ls.py")
    
    st.info("""
    Esta versión ejecuta tu código original **sin modificaciones**.
    
    El programa hará preguntas interactivas una por una, 
    exactamente como en la versión de terminal.
    """)
    
    st.warning("""
    ⚠️ **Advertencia:** Este programa maneja cláusulas simples con su estructura argumental 
    típica, y puede dar resultados inexactos en construcciones que las alteran.
    """)
    
    # Verificar si viene del análisis de aktionsart
    if st.session_state.get('aktionsart_resultado'):
        st.success(f"""
        ✅ **Aktionsart ya identificado:** {st.session_state.aktionsart_resultado.upper()}
        
        **Cláusula:** {st.session_state.oracion_analizada}
        
        **Dinámico:** {'Sí' if st.session_state.get('es_dinamico', False) else 'No'}
        """)
        
        usar_previo = st.radio(
            "¿Deseas usar estos datos?",
            options=["Sí, usar estos datos", "No, ingresar datos nuevos"],
            key="radio_usar_previo"
        )
        
        if usar_previo == "Sí, usar estos datos":
            st.session_state.ls_akt_inicial = st.session_state.aktionsart_resultado
            st.session_state.ls_oracion_inicial = st.session_state.oracion_analizada
            st.session_state.ls_dinamico_inicial = st.session_state.get('es_dinamico', False)
            
            if st.button("▶️ Iniciar generación", type="primary"):
                st.session_state.ls_paso = 'ejecutando'
                st.session_state.ls_capture = StreamlitInputCapture()
                st.rerun()
            return
    
    # Configuración manual
    st.markdown("### 📝 Configuración inicial")
    
    st.write("""
    El programa te hará preguntas adicionales durante la ejecución,
    pero primero necesita estos datos básicos:
    """)
    
    with st.form("form_inicio_wrapper"):
        # Aktionsart
        aktionsart_dict = {
            1: "estado", 2: "estado causativo", 3: "logro", 4: "logro causativo",
            5: "realización", 6: "realización causativa", 7: "semelfactivo",
            8: "semelfactivo causativo", 9: "proceso", 10: "proceso causativo",
            11: "actividad", 12: "actividad causativa", 13: "realización activa",
            14: "realización activa causativa"
        }
        
        akt_num = st.selectbox(
            "Selecciona el aktionsart:",
            options=list(aktionsart_dict.keys()),
            format_func=lambda x: f"{x}. {aktionsart_dict[x]}"
        )
        
        oracion = st.text_input(
            "Cláusula a analizar:",
            placeholder="Ejemplo: Juan rompió el jarrón"
        )
        
        # Verificar dinamicidad
        akt_seleccionado = aktionsart_dict[akt_num]
        if akt_seleccionado in ["actividad", "actividad causativa", "realización activa", "realización activa causativa"]:
            es_dinamico = True
            st.info("✓ Este aktionsart es dinámico por definición")
        elif akt_seleccionado in ["estado", "estado causativo", "realización causativa", "proceso causativo"]:
            es_dinamico = False
            st.info("✓ Este aktionsart no es dinámico por definición")
        else:
            es_dinamico = st.checkbox(
                "¿El predicado es dinámico?",
                help="Compatible con «enérgicamente», «con fuerza», «con ganas»"
            )
        
        iniciar = st.form_submit_button("▶️ Iniciar generación", type="primary")
    
    if iniciar and oracion.strip():
        st.session_state.ls_akt_inicial = akt_seleccionado
        st.session_state.ls_oracion_inicial = oracion.strip()
        st.session_state.ls_dinamico_inicial = es_dinamico
        st.session_state.ls_paso = 'ejecutando'
        st.session_state.ls_capture = StreamlitInputCapture()
        st.rerun()


def paso_ejecutando():
    """Ejecuta el código original y maneja las preguntas interactivas"""
    st.markdown("## 🔄 Generando Estructura Lógica")
    
    # Mostrar configuración inicial
    with st.expander("📋 Configuración inicial", expanded=False):
        st.write(f"**Aktionsart:** {st.session_state.ls_akt_inicial}")
        st.write(f"**Cláusula:** {st.session_state.ls_oracion_inicial}")
        st.write(f"**Dinámico:** {'Sí' if st.session_state.ls_dinamico_inicial else 'No'}")
    
    # Mostrar preguntas respondidas con más detalle
    num_respuestas = len(st.session_state.get('ls_respuestas', {}))
    if num_respuestas > 0:
        with st.expander(f"✅ Preguntas respondidas ({num_respuestas})", expanded=False):
            for i, (key, valor) in enumerate(st.session_state.ls_respuestas.items(), 1):
                st.text(f"{i}. {key}: {valor}")
    
    # Mostrar spinner mientras ejecuta
    with st.spinner('Ejecutando código original...'):
        completado, excepcion = ejecutar_ls_original()
    
    if completado:
        # Ejecución terminada - mostrar resultado
        st.success("✅ Generación completada con éxito")
        
        if 'ls_output' in st.session_state and st.session_state.ls_output:
            st.markdown("### 📄 Resultado:")
            
            # Extraer la estructura lógica del output
            output = st.session_state.ls_output
            
            # Buscar la estructura lógica en el output
            if "La estructura lógica es:" in output:
                lineas = output.split('\n')
                for i, linea in enumerate(lineas):
                    if "La estructura lógica es:" in linea:
                        estructura = linea.split("La estructura lógica es:")[-1].strip()
                        st.code(estructura, language="")
                        break
            else:
                # Mostrar todo el output
                st.text(output)
        
        # Botones de acción
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generar otra estructura"):
                # Limpiar estado
                for key in list(st.session_state.keys()):
                    if key.startswith('ls_'):
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🏠 Volver al inicio"):
                st.session_state.pagina = 'inicio'
                st.rerun()
    
    elif excepcion and isinstance(excepcion, NecesitaInputException):
        # Necesita input del usuario - mostrar la pregunta
        st.markdown("### 💬 El programa necesita información")
        
        # Barra de progreso estimado
        progreso = min(num_respuestas / 10.0, 0.9)  # Máximo 90% hasta terminar
        st.progress(progreso, text=f"Progreso: {num_respuestas} preguntas respondidas")
        
        key = excepcion.key
        
        # Mostrar la pregunta en un formato destacado
        st.info(excepcion.prompt)
        
        # Formulario para la respuesta
        with st.form(key=f"form_{key}", clear_on_submit=False):
            
            if excepcion.tipo == 'texto':
                # Pregunta de texto libre
                respuesta = st.text_input(
                    "Tu respuesta:",
                    key=f"input_{key}",
                    help="Escribe tu respuesta y presiona el botón de abajo"
                )
                
                # Detectar si es una pregunta numérica o específica
                prompt_lower = excepcion.prompt.lower()
                if any(palabra in prompt_lower for palabra in ['número', 'escribe 1', 'escribe 2', '(1)', '(2)', 'indica el']):
                    st.caption("💡 Tip: Esta pregunta espera un número específico como respuesta (ej: 1, 2, 3)")
                elif '0' in excepcion.prompt and 'si no hay' in prompt_lower:
                    st.caption("💡 Tip: Escribe 0 si no hay este elemento, o escribe el elemento si existe")
                
                submit = st.form_submit_button("✓ Enviar respuesta", type="primary", use_container_width=True)
                
                if submit:
                    if respuesta.strip():
                        # Guardar respuesta
                        if 'ls_respuestas' not in st.session_state:
                            st.session_state.ls_respuestas = {}
                        
                        st.session_state.ls_respuestas[key] = respuesta.strip()
                        
                        # Debug: Mostrar que se guardó
                        st.success(f"✓ Respuesta guardada: {respuesta.strip()}")
                        
                        # Forzar rerun
                        st.rerun()
                    else:
                        st.warning("⚠️ Por favor ingresa una respuesta antes de continuar")
            
            elif excepcion.tipo == 'si_no':
                # Pregunta sí/no
                respuesta = st.radio(
                    "Selecciona tu respuesta:",
                    options=["Sí", "No"],
                    key=f"radio_{key}",
                    horizontal=True,
                    index=0
                )
                
                submit = st.form_submit_button("✓ Enviar respuesta", type="primary", use_container_width=True)
                
                if submit:
                    # Guardar respuesta
                    if 'ls_respuestas' not in st.session_state:
                        st.session_state.ls_respuestas = {}
                    
                    st.session_state.ls_respuestas[key] = (respuesta == "Sí")
                    
                    # Debug: Mostrar que se guardó
                    st.success(f"✓ Respuesta guardada: {respuesta}")
                    
                    # Forzar rerun
                    st.rerun()
        
        # Botón para ver debug info
        with st.expander("🔧 Información de debug"):
            st.write(f"**Key de pregunta:** {key}")
            st.write(f"**Tipo:** {excepcion.tipo}")
            st.write(f"**Número de respuestas guardadas:** {num_respuestas}")
            st.write(f"**Respuestas actuales:**")
            st.json(st.session_state.get('ls_respuestas', {}))
        
        # Botón para volver atrás si hay un error
        st.markdown("---")
        if st.button("⬅️ Empezar de nuevo"):
            for key in list(st.session_state.keys()):
                if key.startswith('ls_'):
                    del st.session_state[key]
            st.rerun()
    
    else:
        # Error o situación inesperada
        st.error("❌ Ocurrió un error durante la ejecución")
        
        # Mostrar info de debug
        st.write("**Estado actual:**")
        st.write(f"- Respuestas guardadas: {num_respuestas}")
        st.write(f"- Completado: {completado}")
        st.write(f"- Tipo de excepción: {type(excepcion).__name__ if excepcion else 'None'}")
        
        if st.button("🔄 Reintentar desde el inicio"):
            st.session_state.ls_paso = 'inicio'
            for key in list(st.session_state.keys()):
                if key.startswith('ls_'):
                    del st.session_state[key]
            st.rerun()


# ==================== APLICACIÓN PRINCIPAL ====================

def app_estructura_logica():
    """Aplicación principal del wrapper"""
    inicializar_estado_ls()
    
    # Router de pasos
    if st.session_state.ls_paso == 'inicio':
        paso_inicio_ls()
    elif st.session_state.ls_paso == 'ejecutando':
        paso_ejecutando()
    else:
        st.error(f"Paso desconocido: {st.session_state.ls_paso}")
        if st.button("Reiniciar"):
            st.session_state.ls_paso = 'inicio'
            st.rerun()
