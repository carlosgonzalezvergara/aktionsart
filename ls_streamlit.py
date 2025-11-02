# -*- coding: utf-8 -*-
"""
Módulo de Estructuras Lógicas adaptado para Streamlit
Genera representaciones formales RRG de cláusulas en español
"""

import streamlit as st
from typing import Optional, Dict, List
import time


# Diccionario de aktionsart opciones
AKTIONSART_OPCIONES = {
    "estado": "Estado",
    "estado causativo": "Estado Causativo",
    "logro": "Logro",
    "logro causativo": "Logro Causativo",
    "realización": "Realización",
    "realización causativa": "Realización Causativa",
    "semelfactivo": "Semelfactivo",
    "semelfactivo causativo": "Semelfactivo Causativo",
    "proceso": "Proceso",
    "proceso causativo": "Proceso Causativo",
    "actividad": "Actividad",
    "actividad causativa": "Actividad Causativa",
    "realización activa": "Realización Activa",
    "realización activa causativa": "Realización Activa Causativa"
}

# Modificadores de aktionsart
MODIFICADORES_AKT = {
    "logro": "INGR",
    "realización": "BECOME",
    "proceso": "PROC",
    "semelfactivo": "SEML",
    "logro causativo": "INGR",
    "realización causativa": "BECOME",
    "proceso causativo": "PROC",
    "semelfactivo causativo": "SEML"
}

# Operadores de la capa de cláusula
OPERADORES = [
    {"codigo": "IF", "descripcion": "Fuerza ilocutiva", "ejemplos": "DECL, INT, IMP"},
    {"codigo": "TNS", "descripcion": "Tiempo", "ejemplos": "PAST, PRES, FUT"},
    {"codigo": "ASP", "descripcion": "Aspecto", "ejemplos": "PFV, IMPFV, PROG"},
    {"codigo": "MOD", "descripcion": "Modalidad", "ejemplos": "OBLIG, PERMIS, ABIL"},
    {"codigo": "NEG", "descripcion": "Negación", "ejemplos": "NEG"},
    {"codigo": "EVID", "descripcion": "Evidencialidad", "ejemplos": "VIS, INF, HEARSAY"},
]


def inicializar_estado_ls():
    """Inicializa el estado para el generador de estructuras lógicas"""
    if 'ls_paso' not in st.session_state:
        st.session_state.ls_paso = 'inicio'
    if 'ls_aktionsart' not in st.session_state:
        st.session_state.ls_aktionsart = None
    if 'ls_oracion' not in st.session_state:
        st.session_state.ls_oracion = ""
    if 'ls_es_dinamico' not in st.session_state:
        st.session_state.ls_es_dinamico = False
    if 'ls_argumentos' not in st.session_state:
        st.session_state.ls_argumentos = {'x': '', 'y': '', 'z': ''}
    if 'ls_predicado' not in st.session_state:
        st.session_state.ls_predicado = ""
    if 'ls_estructura' not in st.session_state:
        st.session_state.ls_estructura = ""
    if 'ls_operadores_seleccionados' not in st.session_state:
        st.session_state.ls_operadores_seleccionados = []


def generar_estructura_logica_basica(aktionsart: str, x: str, y: str, z: str, pred: str, es_dinamico: bool) -> str:
    """Genera la estructura lógica básica según el aktionsart"""
    
    operador = MODIFICADORES_AKT.get(aktionsart, "")
    
    # ESTADOS
    if aktionsart == "estado":
        if y == "Ø":
            return f"{pred}' ({x})"
        else:
            return f"{pred}' ({x}, {y})"
    
    # ESTADOS CAUSATIVOS
    elif aktionsart == "estado causativo":
        return f"[do' ({x}, Ø)] CAUSE [{pred}' ({y})]"
    
    # LOGROS
    elif aktionsart == "logro":
        if y == "Ø":
            return f"{operador} {pred}' ({x})"
        else:
            return f"{operador} {pred}' ({x}, {y})"
    
    # LOGROS CAUSATIVOS
    elif aktionsart == "logro causativo":
        return f"[do' ({x}, Ø)] CAUSE [{operador} {pred}' ({y})]"
    
    # SEMELFACTIVOS
    elif aktionsart == "semelfactivo":
        return f"{operador} do' ({x}, [{pred}' ({x})])"
    
    # SEMELFACTIVOS CAUSATIVOS
    elif aktionsart == "semelfactivo causativo":
        return f"[do' ({x}, Ø)] CAUSE [{operador} do' ({y}, [{pred}' ({y})])]"
    
    # REALIZACIONES
    elif aktionsart == "realización":
        if y == "Ø":
            return f"{operador} {pred}' ({x})"
        else:
            return f"{operador} {pred}' ({x}, {y})"
    
    # REALIZACIONES CAUSATIVAS
    elif aktionsart == "realización causativa":
        return f"[do' ({x}, Ø)] CAUSE [{operador} {pred}' ({y})]"
    
    # REALIZACIONES ACTIVAS
    elif aktionsart == "realización activa":
        if y == "Ø":
            return f"do' ({x}, [{pred}' ({x})]) & {operador} {pred}' ({x})"
        else:
            return f"do' ({x}, [{pred}' ({x}, ({y}))]) & {operador} {pred}' ({y})"
    
    # REALIZACIONES ACTIVAS CAUSATIVAS
    elif aktionsart == "realización activa causativa":
        return f"[do' ({x}, Ø)] CAUSE [do' ({y}, [{pred}' ({y})]) & {operador} {pred}' ({y})]"
    
    # ACTIVIDADES
    elif aktionsart == "actividad":
        if y == "Ø":
            return f"do' ({x}, [{pred}' ({x})])"
        else:
            return f"do' ({x}, [{pred}' ({x}, {y})])"
    
    # ACTIVIDADES CAUSATIVAS
    elif aktionsart == "actividad causativa":
        return f"[do' ({x}, Ø)] CAUSE [do' ({y}, [{pred}' ({y})])]"
    
    # PROCESOS
    elif aktionsart == "proceso":
        if y == "Ø":
            return f"{operador} {pred}' ({x})"
        else:
            return f"{operador} {pred}' ({x}, {y})"
    
    # PROCESOS CAUSATIVOS
    elif aktionsart == "proceso causativo":
        return f"[do' ({x}, Ø)] CAUSE [{operador} {pred}' ({y})]"
    
    else:
        return f"predicate' ({x}, {y})"


def aplicar_DO(oracion: str, x: str, estructura: str, es_dinamico: bool, aktionsart: str) -> str:
    """Aplica la capa de intencionalidad DO si corresponde"""
    
    # No aplicar DO a estados
    if "estado" in aktionsart:
        return estructura
    
    # Preguntar si la acción fue intencional
    st.write("### 🎯 Intencionalidad")
    intencional = st.radio(
        f"¿«{x[0].upper() + x[1:]}» actuó de manera **intencional** en «{oracion}»?",
        options=["Sí", "No"],
        key="radio_intencional",
        help="Solo acciones realizadas voluntariamente requieren el operador DO"
    )
    
    if intencional == "Sí":
        return f"DO ({estructura})"
    else:
        return estructura


def paso_inicio_ls():
    """Paso inicial del generador de estructuras lógicas"""
    st.markdown("## 📐 Generador de Estructuras Lógicas")
    
    st.write("""
    Este generador te ayudará a formalizar la estructura lógica de una cláusula 
    en la notación de la **Gramática de Papel y Referencia (RRG)**.
    """)
    
    st.info("""
    ⚠️ **Advertencia:** Este programa maneja cláusulas simples con su estructura argumental 
    típica, y puede dar resultados inexactos en construcciones que las alteran 
    (pasivas, antipassivas, etc.).
    """)
    
    # Verificar si viene del análisis de aktionsart
    if st.session_state.get('aktionsart_resultado'):
        st.success(f"""
        ✅ **Aktionsart ya identificado:** {st.session_state.aktionsart_resultado.upper()}
        
        **Cláusula:** {st.session_state.oracion_analizada}
        """)
        
        usar_previo = st.radio(
            "¿Deseas usar estos datos?",
            options=["Sí, usar estos datos", "No, ingresar datos nuevos"],
            key="radio_usar_previo"
        )
        
        if usar_previo == "Sí, usar estos datos":
            st.session_state.ls_aktionsart = st.session_state.aktionsart_resultado
            st.session_state.ls_oracion = st.session_state.oracion_analizada
            st.session_state.ls_es_dinamico = st.session_state.get('es_dinamico', False)
            st.session_state.ls_paso = 'argumentos'
            if st.button("▶️ Continuar con estos datos", type="primary"):
                st.rerun()
            return
    
    # Selección manual
    st.markdown("### 📝 Ingresa los datos de tu cláusula")
    
    with st.form("form_inicio_ls"):
        aktionsart = st.selectbox(
            "Selecciona el aktionsart del predicado:",
            options=list(AKTIONSART_OPCIONES.keys()),
            format_func=lambda x: AKTIONSART_OPCIONES[x]
        )
        
        oracion = st.text_input(
            "Escribe la cláusula completa:",
            placeholder="Ejemplo: Juan rompió el jarrón"
        )
        
        # Solo preguntar dinamicidad si no es un estado
        es_dinamico = False
        if "estado" not in aktionsart:
            es_dinamico = st.checkbox(
                "¿El predicado es dinámico? (requiere energía/esfuerzo del agente)",
                help="Ejemplos dinámicos: correr, empujar. Ejemplos no dinámicos: caer, derretirse"
            )
        
        continuar = st.form_submit_button("▶️ Continuar", type="primary")
    
    if continuar and oracion.strip():
        st.session_state.ls_aktionsart = aktionsart
        st.session_state.ls_oracion = oracion.strip()
        st.session_state.ls_es_dinamico = es_dinamico
        st.session_state.ls_paso = 'argumentos'
        st.rerun()


def paso_argumentos():
    """Solicitar los argumentos de la cláusula"""
    st.markdown("## 📋 Argumentos de la Cláusula")
    
    st.write(f"Estamos analizando: **«{st.session_state.ls_oracion}»**")
    
    st.info("""
    **Instrucciones:**
    - Identifica los argumentos principales del verbo
    - Usa **Ø** (letra O con barra) para argumentos vacíos o no expresados
    - Usa nombres genéricos o las palabras exactas de la cláusula
    """)
    
    with st.form("form_argumentos"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Argumentos principales")
            x = st.text_input(
                "**x** (típicamente el sujeto/agente):",
                placeholder="Ejemplo: Juan, el gato, Ø",
                help="El primer argumento, usualmente quien realiza la acción"
            )
            
            y = st.text_input(
                "**y** (típicamente el paciente/tema):",
                placeholder="Ejemplo: el jarrón, un libro, Ø",
                help="El segundo argumento, usualmente lo afectado por la acción"
            )
        
        with col2:
            st.markdown("### Argumento adicional")
            z = st.text_input(
                "**z** (tercer argumento, si existe):",
                placeholder="Ejemplo: a María, Ø",
                help="Tercer argumento, como objeto indirecto (opcional)"
            )
            
            st.markdown("### Predicado")
            pred = st.text_input(
                "**predicado** (verbo en infinitivo inglés o español):",
                placeholder="Ejemplo: break, romper, run",
                help="El verbo principal en forma de predicado"
            )
        
        col_back, col_cont = st.columns([1, 4])
        with col_back:
            volver = st.form_submit_button("⬅️ Volver")
        with col_cont:
            continuar = st.form_submit_button("▶️ Generar estructura", type="primary")
    
    if volver:
        st.session_state.ls_paso = 'inicio'
        st.rerun()
    
    if continuar:
        if not all([x, y, pred]):
            st.error("⚠️ Por favor completa al menos x, y, y el predicado.")
        else:
            st.session_state.ls_argumentos = {'x': x, 'y': y, 'z': z if z else 'Ø'}
            st.session_state.ls_predicado = pred
            st.session_state.ls_paso = 'generar'
            st.rerun()


def paso_generar():
    """Generar y mostrar la estructura lógica"""
    st.markdown("## ✨ Estructura Lógica Generada")
    
    # Obtener datos
    akt = st.session_state.ls_aktionsart
    oracion = st.session_state.ls_oracion
    args = st.session_state.ls_argumentos
    pred = st.session_state.ls_predicado
    es_dinamico = st.session_state.ls_es_dinamico
    
    # Mostrar información
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Cláusula:** {oracion}
        
        **Aktionsart:** {AKTIONSART_OPCIONES[akt]}
        """)
    with col2:
        st.info(f"""
        **Argumentos:**
        - x = {args['x']}
        - y = {args['y']}
        - z = {args['z']}
        
        **Predicado:** {pred}'
        """)
    
    # Generar estructura básica
    estructura = generar_estructura_logica_basica(
        akt, args['x'], args['y'], args['z'], pred, es_dinamico
    )
    
    # Aplicar DO si corresponde
    if args['x'] != 'Ø' and "estado" not in akt:
        estructura = aplicar_DO(oracion, args['x'], estructura, es_dinamico, akt)
        if st.button("Actualizar con intencionalidad"):
            st.rerun()
    
    # Mostrar estructura
    st.markdown("### 🎯 Estructura lógica del núcleo:")
    st.code(estructura, language="")
    
    st.session_state.ls_estructura = estructura
    
    # Opción de añadir operadores
    st.markdown("---")
    st.markdown("### ➕ Capa de Operadores (Opcional)")
    
    st.write("""
    Puedes añadir operadores de la **capa de cláusula** para expresar 
    tiempo, aspecto, modalidad, etc.
    """)
    
    operadores_seleccionados = []
    
    with st.expander("🔧 Añadir operadores"):
        for op in OPERADORES:
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                añadir = st.checkbox(
                    op["codigo"],
                    key=f"op_{op['codigo']}"
                )
            
            with col2:
                st.write(f"*{op['descripcion']}*")
            
            with col3:
                if añadir:
                    valor = st.text_input(
                        "Valor:",
                        placeholder=op["ejemplos"].split(",")[0].strip(),
                        key=f"val_{op['codigo']}"
                    )
                    if valor:
                        operadores_seleccionados.append(f"{op['codigo']}: {valor}")
    
    # Mostrar estructura final con operadores
    if operadores_seleccionados:
        st.markdown("### 🎯 Estructura lógica completa:")
        operadores_str = ", ".join(operadores_seleccionados)
        estructura_completa = f"({operadores_str}) ({estructura})"
        st.code(estructura_completa, language="")
    
    # Opciones finales
    st.markdown("---")
    st.write("### 🎯 ¿Qué deseas hacer ahora?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Analizar otra cláusula"):
            for key in list(st.session_state.keys()):
                if key.startswith('ls_'):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📋 Copiar estructura"):
            st.info("Copia la estructura desde el cuadro de código arriba ⬆️")
    
    with col3:
        if st.button("🏠 Volver al inicio"):
            st.session_state.pagina = 'inicio'
            st.rerun()


def app_estructura_logica():
    """Aplicación principal del generador de estructuras lógicas"""
    inicializar_estado_ls()
    
    # Router de pasos
    if st.session_state.ls_paso == 'inicio':
        paso_inicio_ls()
    elif st.session_state.ls_paso == 'argumentos':
        paso_argumentos()
    elif st.session_state.ls_paso == 'generar':
        paso_generar()
