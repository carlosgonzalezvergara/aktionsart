# -*- coding: utf-8 -*-
"""
Aplicación Streamlit para análisis de Aktionsart y Estructuras Lógicas
Basada en la Gramática de Papel y Referencia (RRG)
"""

import streamlit as st
from typing import Optional
import time

# Configuración de la página
st.set_page_config(
    page_title="Analizador Lingüístico RRG",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos personalizados (versiones adaptadas)
from aktionsart_streamlit import app_aktionsart
from ls_streamlit import app_estructura_logica

# CSS personalizado para mejorar la apariencia
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
    </style>
""", unsafe_allow_html=True)


def inicializar_estado():
    """Inicializa las variables de estado de la sesión"""
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'inicio'
    if 'aktionsart_resultado' not in st.session_state:
        st.session_state.aktionsart_resultado = None
    if 'oracion_analizada' not in st.session_state:
        st.session_state.oracion_analizada = None


def pagina_inicio():
    """Página principal con el menú de opciones"""
    st.markdown('<h1 class="main-header">🔍 Analizador Lingüístico RRG</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Asistente para la detección de aktionsart y '
        'formalización de estructuras lógicas</p>',
        unsafe_allow_html=True
    )
    
    # Información sobre RRG
    with st.expander("ℹ️ ¿Qué es la Gramática de Papel y Referencia (RRG)?"):
        st.write("""
        La **Role and Reference Grammar (RRG)** es un modelo de gramática funcional 
        que analiza la estructura de las lenguas desde una perspectiva semántico-sintáctica.
        
        Esta herramienta te ayuda a:
        - **Identificar el aktionsart** (aspecto léxico) de predicados verbales
        - **Generar estructuras lógicas** formales de cláusulas en español
        - **Analizar rasgos semánticos** como causatividad, telicidad, dinamicidad, etc.
        """)
    
    st.markdown("---")
    
    # Opciones principales
    st.markdown("### 📋 ¿Qué deseas hacer?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Opción 1")
        st.markdown("**Identificar el aktionsart de un predicado**")
        st.write("Analiza un verbo mediante pruebas lingüísticas y obtén su clasificación aspectual.")
        if st.button("🚀 Iniciar análisis de Aktionsart", key="btn_aktionsart"):
            st.session_state.pagina = 'aktionsart'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### 📐 Opción 2")
        st.markdown("**Obtener la estructura lógica de una cláusula**")
        st.write("Genera la representación formal en notación RRG (si ya conoces el aktionsart).")
        if st.button("🚀 Generar estructura lógica", key="btn_ls"):
            st.session_state.pagina = 'estructura_logica'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Información adicional
    st.markdown("---")
    with st.expander("📚 Sobre esta herramienta"):
        st.write("""
        **Desarrollada para el análisis lingüístico del español**
        
        Esta aplicación implementa pruebas diagnósticas basadas en:
        - Vendler (1967) - Clasificación aspectual de verbos
        - Van Valin & LaPolla (1997) - Sintaxis RRG
        - Van Valin (2005) - Explorando la sintaxis RRG
        
        **Tipos de aktionsart identificados:**
        - Estados y estados causativos
        - Logros y logros causativos
        - Semelfactivos
        - Realizaciones (activas y no activas)
        - Actividades
        - Procesos
        
        **Rasgos analizados:**
        - [±causativo], [±estativo], [±puntual], [±télico], [±dinámico]
        """)


def main():
    """Función principal que controla el flujo de la aplicación"""
    inicializar_estado()
    
    # Sidebar con navegación
    with st.sidebar:
        st.markdown("## 🧭 Navegación")
        
        if st.button("🏠 Volver al inicio"):
            st.session_state.pagina = 'inicio'
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Estado actual")
        st.info(f"**Página:** {st.session_state.pagina.replace('_', ' ').title()}")
        
        if st.session_state.aktionsart_resultado:
            st.success("✅ Aktionsart identificado")
        
        st.markdown("---")
        st.markdown("### ℹ️ Ayuda")
        with st.expander("¿Cómo usar esta herramienta?"):
            st.write("""
            1. Selecciona una opción en el menú principal
            2. Sigue las instrucciones paso a paso
            3. Responde las preguntas con atención
            4. Obtén tu resultado formalizado
            """)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        <p>Herramienta académica para<br>análisis lingüístico RRG</p>
        <p>© 2024</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Routing entre páginas
    if st.session_state.pagina == 'inicio':
        pagina_inicio()
    elif st.session_state.pagina == 'aktionsart':
        app_aktionsart()
    elif st.session_state.pagina == 'estructura_logica':
        app_estructura_logica()


if __name__ == "__main__":
    main()
