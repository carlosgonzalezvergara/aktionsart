# -*- coding: utf-8 -*-
"""
Módulo de Aktionsart adaptado para Streamlit
Identifica el aspecto léxico de predicados verbales mediante pruebas lingüísticas
"""

import streamlit as st
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import time


class Aktionsart(Enum):
    ESTADO = "estado"
    ESTADO_CAUSATIVO = "estado causativo"
    LOGRO = "logro"
    LOGRO_CAUSATIVO = "logro causativo"
    SEMELFACTIVO = "semelfactivo"
    SEMELFACTIVO_CAUSATIVO = "semelfactivo causativo"
    REALIZACION_ACTIVA = "realización activa"
    REALIZACION_ACTIVA_CAUSATIVA = "realización activa causativa"
    REALIZACION = "realización"
    REALIZACION_CAUSATIVA = "realización causativa"
    ACTIVIDAD = "actividad"
    ACTIVIDAD_CAUSATIVA = "actividad causativa"
    PROCESO = "proceso"
    PROCESO_CAUSATIVO = "proceso causativo"


@dataclass
class RasgosPred:
    causativo: bool = False
    estativo: bool = False
    puntual: bool = False
    telico: bool = False
    dinamico: bool = False


@dataclass
class DatosClause:
    gerundio: str = ""
    participio: str = ""
    infinitivo: str = ""
    sujeto: str = ""
    complementos: str = ""
    persona_numero: str = ""
    rasgos_obtenidos: bool = False


# Diccionarios de conjugación
ESTAR = {
    '1s': "estoy", '2s': "estás", '3s': "está",
    '1p': "estamos", '2p': "están/estáis", '3p': "están"
}

ESTAR_PRETERITO = {
    '1s': "estuve", '2s': "estuviste", '3s': "estuvo",
    '1p': "estuvimos", '2p': "estuvieron/estuvisteis", '3p': "estuvieron"
}

ESTAR_SUBJUNTIVO = {
    '1s': "estuviera", '2s': "estuvieras", '3s': "estuviera",
    '1p': "estuviéramos", '2p': "estuvieran/estuvierais", '3p': "estuvieran"
}

HABER = {
    '1s': "he", '2s': "has", '3s': "ha",
    '1p': "hemos", '2p': "han/habéis", '3p': "han"
}

DEJAR = {
    '1s': "dejara", '2s': "dejaras", '3s': "dejara",
    '1p': "dejáramos", '2p': "dejaran/dejarais", '3p': "dejaran"
}


def construir_perif_gerundio(tiempo: str, datos: DatosClause) -> str:
    """Construye perífrasis con gerundio"""
    forma_estar = ESTAR_PRETERITO[datos.persona_numero] if tiempo == 'preterito' else ESTAR[datos.persona_numero]
    return " ".join(parte for parte in [datos.sujeto, f"{forma_estar} {datos.gerundio}", datos.complementos] if parte)


def construir_perif_gerundio_subj(datos: DatosClause) -> str:
    """Construye perífrasis con gerundio en subjuntivo"""
    forma_estar = ESTAR_SUBJUNTIVO[datos.persona_numero]
    return " ".join(parte for parte in [datos.sujeto, f"{forma_estar} {datos.gerundio}", datos.complementos] if parte)


def construir_perif_participio(datos: DatosClause) -> str:
    """Construye perífrasis con participio"""
    forma_haber = HABER[datos.persona_numero]
    return " ".join(parte for parte in [datos.sujeto, f"{forma_haber} {datos.participio}", datos.complementos] if parte)


def construir_perif_infinitivo(datos: DatosClause) -> str:
    """Construye perífrasis con infinitivo"""
    forma_dejar = DEJAR[datos.persona_numero]
    return " ".join(parte for parte in [f"{forma_dejar} de {datos.infinitivo}", datos.complementos] if parte)


def determinar_subtipo(pred_es: RasgosPred) -> Optional[str]:
    """Determina el subtipo de aktionsart basado en rasgos"""
    if pred_es.estativo:
        return "ESTADO"
    elif pred_es.puntual and pred_es.telico:
        return "LOGRO"
    elif pred_es.puntual and not pred_es.telico:
        return "SEMELFACTIVO"
    elif not pred_es.puntual and pred_es.telico and pred_es.dinamico:
        return "REALIZACION_ACTIVA"
    elif not pred_es.puntual and not pred_es.telico and pred_es.dinamico:
        return "ACTIVIDAD"
    elif not pred_es.puntual and pred_es.telico and not pred_es.dinamico:
        return "REALIZACION"
    elif not pred_es.puntual and not pred_es.telico and not pred_es.dinamico:
        return "PROCESO"
    else:
        return None


def determinar_aktionsart(pred_es: RasgosPred) -> Optional[Aktionsart]:
    """Determina el aktionsart final considerando causatividad"""
    subtipo = determinar_subtipo(pred_es)
    if subtipo is None:
        return None
    if pred_es.causativo:
        if subtipo in ["REALIZACION", "REALIZACION_ACTIVA", "ACTIVIDAD"]:
            return Aktionsart[f"{subtipo}_CAUSATIVA"]
        else:
            return Aktionsart[f"{subtipo}_CAUSATIVO"]
    else:
        return Aktionsart[subtipo]


def inicializar_estado_akt():
    """Inicializa el estado específico del análisis de aktionsart"""
    if 'akt_paso' not in st.session_state:
        st.session_state.akt_paso = 'inicio'
    if 'akt_oracion' not in st.session_state:
        st.session_state.akt_oracion = ""
    if 'akt_rasgos' not in st.session_state:
        st.session_state.akt_rasgos = RasgosPred()
    if 'akt_datos' not in st.session_state:
        st.session_state.akt_datos = DatosClause()
    if 'akt_evento_basico' not in st.session_state:
        st.session_state.akt_evento_basico = ""
    if 'akt_resultado' not in st.session_state:
        st.session_state.akt_resultado = None


def paso_inicio():
    """Paso inicial: solicitar la cláusula"""
    st.markdown("## 🎯 Identificación de Aktionsart")
    st.write("""
    Este analizador te guiará a través de una serie de **pruebas lingüísticas** 
    para identificar el aktionsart (aspecto léxico) del predicado principal de tu cláusula.
    """)
    
    st.markdown("### 📝 Ingresa tu cláusula")
    st.info("""
    **Instrucciones:**
    - Escribe una cláusula con el verbo conjugado en **pretérito** (ej: «Pedro corrió hasta su casa»)
    - Si suena muy extraña en pretérito, escríbela en **presente** (ej: «María sabe inglés»)
    """)
    
    oracion = st.text_input(
        "Cláusula a analizar:",
        placeholder="Ejemplo: Juan rompió el jarrón",
        key="input_oracion"
    )
    
    if st.button("▶️ Comenzar análisis", disabled=not oracion.strip()):
        st.session_state.akt_oracion = oracion.strip()
        st.session_state.akt_paso = 'causatividad'
        st.rerun()


def paso_causatividad():
    """Prueba de causatividad"""
    st.markdown("## 🧪 PRUEBA DE CAUSATIVIDAD")
    
    oracion = st.session_state.akt_oracion
    
    st.write(f"Estamos analizando: **«{oracion}»**")
    st.markdown("---")
    
    st.write("### Intenta reformular tu cláusula siguiendo estos modelos:")
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ El gato rompió el jarrón")
        st.info("→ El gato **HIZO QUE** el jarrón se rompiera")
    with col2:
        st.success("✅ Ana le dio un libro a Pepe")
        st.info("→ Ana **HIZO QUE** Pepe tuviera un libro")
    
    st.markdown("---")
    reformulacion = st.text_area(
        "Escribe tu reformulación (o deja en blanco si no es posible):",
        key="reformulacion",
        placeholder="Escribe tu reformulación aquí..."
    )
    
    es_causativo = False
    
    if reformulacion.strip():
        st.write("### ✅ Verifica que tu reformulación cumple estos criterios:")
        st.markdown(f"""
        1. «**{reformulacion[0].upper() + reformulacion[1:]}**» debe mantener el significado de «{oracion}»
        2. No debe añadir nuevos argumentos ni repetir otros ya existentes
        3. El complemento directo de «{oracion}» debe sufrir un cambio de estado
        4. No debe tratarse de expresiones de consumo o creación
        """)
        
        es_causativo = st.radio(
            "¿Tu reformulación cumple con todos estos criterios?",
            options=["Sí", "No"],
            key="radio_causativo"
        ) == "Sí"
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'inicio'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary"):
            st.session_state.akt_rasgos.causativo = es_causativo
            
            if es_causativo and reformulacion.strip():
                st.session_state.akt_paso = 'evento_basico'
            else:
                st.session_state.akt_paso = 'estatividad'
            st.rerun()


def paso_evento_basico():
    """Solicitar el evento básico para predicados causativos"""
    st.markdown("## 📋 Evento Básico")
    
    st.info("""
    Como tu predicado es **causativo**, necesitamos identificar el evento o estado resultante 
    **sin la causa**.
    """)
    
    st.write("### Ejemplos:")
    st.markdown("""
    - Si analizaste «El gato rompió el jarrón» → escribe: **«el jarrón se rompió»**
    - Si analizaste «Ana le dio un libro a Pepe» → escribe: **«Pepe tiene un libro»**
    """)
    
    evento = st.text_input(
        "Escribe el evento o estado resultante:",
        key="input_evento",
        placeholder="Ejemplo: el jarrón se rompió"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'causatividad'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary", disabled=not evento.strip()):
            st.session_state.akt_evento_basico = evento.strip()
            # Cambiamos la oración a analizar por el evento básico
            st.session_state.akt_oracion = evento.strip()
            st.session_state.akt_paso = 'estatividad'
            st.rerun()


def paso_estatividad():
    """Prueba de estatividad"""
    st.markdown("## 🧪 PRUEBA DE ESTATIVIDAD")
    
    oracion = st.session_state.akt_oracion
    
    st.write("### Observa el siguiente diálogo:")
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
    <p><strong>—¿Qué pasó hace un rato / ayer / el mes pasado?</strong></p>
    <p><strong>—{oracion[0].upper() + oracion[1:]}.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    es_buena_respuesta = st.radio(
        "¿Te parece que tu cláusula es una buena respuesta a la pregunta? (con cualquiera de las opciones temporales)",
        options=["Sí", "No"],
        key="radio_estatividad"
    )
    
    st.info("""
    💡 **Pista:** Los predicados estativos (como «saber», «tener», «estar») 
    generalmente NO son buenas respuestas a «¿Qué pasó?»
    """)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'causatividad' if not st.session_state.akt_rasgos.causativo else 'evento_basico'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary"):
            # La estatividad es el INVERSO de la respuesta
            st.session_state.akt_rasgos.estativo = (es_buena_respuesta == "No")
            
            if st.session_state.akt_rasgos.estativo:
                # Si es estativo, saltamos a los resultados
                st.session_state.akt_paso = 'resultado'
            else:
                # Si no es estativo, necesitamos obtener info de la cláusula
                st.session_state.akt_paso = 'info_clausula'
            st.rerun()


def paso_info_clausula():
    """Recopilar información morfosintáctica de la cláusula"""
    st.markdown("## 📋 Información de la Cláusula")
    
    oracion = st.session_state.akt_oracion
    
    st.write(f"Estamos analizando: **«{oracion}»**")
    st.info("Necesitamos información morfológica del verbo para realizar las siguientes pruebas.")
    
    with st.form("form_info_clausula"):
        infinitivo = st.text_input(
            "INFINITIVO del verbo (incluyendo clíticos si los hay):",
            placeholder="Ejemplos: derretirse, decirle, correr"
        )
        
        gerundio = st.text_input(
            "GERUNDIO del verbo (sin clíticos):",
            placeholder="Ejemplos: derritiendo, corriendo"
        )
        
        participio = st.text_input(
            "PARTICIPIO del verbo (masculino singular):",
            placeholder="Ejemplos: derretido, corrido"
        )
        
        sujeto = st.text_input(
            "Todo lo que hay ANTES del verbo (incluyendo clíticos). Escribe '0' si no hay nada:",
            placeholder="Ejemplos: Pedro, La niña, 0"
        )
        
        complementos = st.text_input(
            "Todo lo que hay DESPUÉS del verbo. Escribe '0' si no hay nada:",
            placeholder="Ejemplos: hasta su casa, un libro, 0"
        )
        
        persona_numero = st.selectbox(
            "Persona y número del verbo:",
            options=['1s', '2s', '3s', '1p', '2p', '3p'],
            format_func=lambda x: {
                '1s': '1ª persona singular (yo)',
                '2s': '2ª persona singular (tú)',
                '3s': '3ª persona singular (él/ella)',
                '1p': '1ª persona plural (nosotros)',
                '2p': '2ª persona plural (vosotros/ustedes)',
                '3p': '3ª persona plural (ellos/ellas)'
            }[x]
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            volver = st.form_submit_button("⬅️ Volver")
        with col2:
            continuar = st.form_submit_button("Continuar ➡️", type="primary")
    
    if volver:
        st.session_state.akt_paso = 'estatividad'
        st.rerun()
    
    if continuar:
        if not all([infinitivo, gerundio, participio]):
            st.error("⚠️ Por favor completa al menos el infinitivo, gerundio y participio.")
        else:
            st.session_state.akt_datos.infinitivo = infinitivo
            st.session_state.akt_datos.gerundio = gerundio
            st.session_state.akt_datos.participio = participio
            st.session_state.akt_datos.sujeto = "" if sujeto == "0" else sujeto
            st.session_state.akt_datos.complementos = "" if complementos == "0" else complementos
            st.session_state.akt_datos.persona_numero = persona_numero
            st.session_state.akt_datos.rasgos_obtenidos = True
            st.session_state.akt_paso = 'duratividad'
            st.rerun()


def paso_duratividad():
    """Prueba de puntualidad/duratividad"""
    st.markdown("## 🧪 PRUEBA DE PUNTUALIDAD")
    
    datos = st.session_state.akt_datos
    perifrasis = construir_perif_gerundio('preterito', datos)
    
    st.write("### Observa esta expresión:")
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
    <p style='font-size: 1.1rem;'><strong>«{perifrasis[0].upper() + perifrasis[1:]} durante una hora / un mes»</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    es_posible = st.radio(
        "¿Es esta una expresión posible? (sin que el evento tome una interpretación iterativa o de inminencia)",
        options=["Sí", "No"],
        key="radio_duratividad",
        help="Si puedes decir naturalmente la frase con 'durante', el evento es durativo (no puntual)"
    )
    
    st.info("""
    💡 **Pista:** 
    - Eventos **puntuales**: tocar la puerta, alcanzar la cima (NO aceptan 'durante')
    - Eventos **durativos**: correr, trabajar, derretirse (SÍ aceptan 'durante')
    """)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'info_clausula'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary"):
            # Puntual es el INVERSO de durativo
            st.session_state.akt_rasgos.puntual = (es_posible == "No")
            st.session_state.akt_paso = 'telicidad'
            st.rerun()


def paso_telicidad():
    """Prueba de telicidad"""
    st.markdown("## 🧪 PRUEBA DE TELICIDAD")
    
    datos = st.session_state.akt_datos
    perif_gerundio = construir_perif_gerundio_subj(datos)
    perif_participio = construir_perif_participio(datos)
    perif_infinitivo = construir_perif_infinitivo(datos)
    
    st.write("### Imagina la siguiente situación:")
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 5px; margin: 1rem 0;'>
    <p><strong>Imagina que {perif_gerundio} y de pronto {perif_infinitivo}.</strong></p>
    <p style='margin-top: 1rem;'>En esa situación, ¿se podría decir que <strong>«{perif_participio}»</strong>?</p>
    </div>
    """, unsafe_allow_html=True)
    
    se_puede_decir = st.radio(
        "¿Se podría decir eso?",
        options=["Sí", "No"],
        key="radio_telicidad"
    )
    
    st.info("""
    💡 **Pista:** 
    - Eventos **télicos** (con punto final): Si lo interrumpes, NO se ha completado
    - Eventos **atélicos** (sin punto final): Si lo interrumpes, SÍ se puede decir que ocurrió
    
    Ejemplo télico: «construir una casa» - si lo dejas a medias, NO has construido la casa
    Ejemplo atélico: «correr» - si dejas de correr, SÍ corriste
    """)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'duratividad'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary"):
            # Télico es el INVERSO de la respuesta
            st.session_state.akt_rasgos.telico = (se_puede_decir == "No")
            st.session_state.akt_paso = 'dinamicidad'
            st.rerun()


def paso_dinamicidad():
    """Prueba de dinamicidad"""
    st.markdown("## 🧪 PRUEBA DE DINAMICIDAD")
    
    datos = st.session_state.akt_datos
    perifrasis = construir_perif_gerundio('presente', datos)
    
    st.write("### Observa esta expresión:")
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 1rem 0;'>
    <p style='font-size: 1.1rem;'><strong>«{perifrasis[0].upper() + perifrasis[1:]} enérgicamente / con fuerza / con ganas»</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    es_compatible = st.radio(
        "¿Esta expresión es compatible con alguna de las opciones?",
        options=["Sí", "No"],
        key="radio_dinamicidad"
    )
    
    st.info("""
    💡 **Pista:** 
    - Eventos **dinámicos**: implican gasto de energía (correr, empujar, trabajar)
    - Eventos **no dinámicos**: ocurren sin esfuerzo agentivo (caer, derretirse, envejecer)
    """)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver"):
            st.session_state.akt_paso = 'telicidad'
            st.rerun()
    with col2:
        if st.button("Continuar ➡️", type="primary"):
            st.session_state.akt_rasgos.dinamico = (es_compatible == "Sí")
            st.session_state.akt_paso = 'resultado'
            st.rerun()


def paso_resultado():
    """Mostrar el resultado del análisis"""
    st.markdown("## 🎊 RESULTADO DEL ANÁLISIS")
    
    rasgos = st.session_state.akt_rasgos
    aktionsart = determinar_aktionsart(rasgos)
    
    if aktionsart is None:
        st.error("""
        ❌ No se pudo identificar el aktionsart con estos parámetros.
        Por favor, revisa tus respuestas con cuidado.
        """)
        if st.button("🔄 Intentar de nuevo"):
            # Reiniciar
            for key in list(st.session_state.keys()):
                if key.startswith('akt_'):
                    del st.session_state[key]
            st.rerun()
        return
    
    oracion_original = st.session_state.akt_evento_basico if st.session_state.akt_evento_basico else st.session_state.akt_oracion
    
    st.success(f"""
    ### ✅ El aktionsart del predicado de «{oracion_original}» es:
    # {aktionsart.value.upper()}
    """)
    
    # Mostrar rasgos
    akt_estado = aktionsart in [Aktionsart.ESTADO, Aktionsart.ESTADO_CAUSATIVO]
    
    st.markdown("### 📊 Rasgos identificados:")
    
    cols = st.columns(5)
    rasgos_info = [
        ("Causativo", rasgos.causativo),
        ("Estativo", rasgos.estativo),
        ("Puntual", False if akt_estado else rasgos.puntual),
        ("Télico", False if akt_estado else rasgos.telico),
        ("Dinámico", False if akt_estado else rasgos.dinamico)
    ]
    
    for col, (nombre, valor) in zip(cols, rasgos_info):
        with col:
            icono = "✅" if valor else "❌"
            simbolo = "+" if valor else "-"
            st.metric(nombre, f"[{simbolo}]", delta=icono)
    
    # Guardar en session_state global
    st.session_state.aktionsart_resultado = aktionsart.value
    st.session_state.oracion_analizada = oracion_original
    st.session_state.es_dinamico = False if akt_estado else rasgos.dinamico
    
    st.markdown("---")
    st.write("### 🎯 ¿Qué deseas hacer ahora?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Analizar otra cláusula"):
            # Reiniciar solo el estado de aktionsart
            for key in list(st.session_state.keys()):
                if key.startswith('akt_'):
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("📐 Obtener estructura lógica"):
            st.session_state.pagina = 'estructura_logica'
            st.rerun()
    
    with col3:
        if st.button("🏠 Volver al inicio"):
            st.session_state.pagina = 'inicio'
            st.rerun()


def app_aktionsart():
    """Aplicación principal de aktionsart"""
    inicializar_estado_akt()
    
    # Router de pasos
    if st.session_state.akt_paso == 'inicio':
        paso_inicio()
    elif st.session_state.akt_paso == 'causatividad':
        paso_causatividad()
    elif st.session_state.akt_paso == 'evento_basico':
        paso_evento_basico()
    elif st.session_state.akt_paso == 'estatividad':
        paso_estatividad()
    elif st.session_state.akt_paso == 'info_clausula':
        paso_info_clausula()
    elif st.session_state.akt_paso == 'duratividad':
        paso_duratividad()
    elif st.session_state.akt_paso == 'telicidad':
        paso_telicidad()
    elif st.session_state.akt_paso == 'dinamicidad':
        paso_dinamicidad()
    elif st.session_state.akt_paso == 'resultado':
        paso_resultado()
