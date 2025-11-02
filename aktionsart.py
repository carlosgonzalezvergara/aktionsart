# -*- coding: utf-8 -*-
import locale
import logging
import readline
import subprocess
import time
import sys
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Respuesta(Enum):
    SI = ["sí", "si", "s"]
    NO = ["no", "n"]


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


ESTAR = {
    '1s': "estoy",
    '2s': "estás",
    '3s': "está",
    '1p': "estamos",
    '2p': "están/estáis",
    '3p': "están"
}

ESTAR_PRETERITO = {
    '1s': "estuve",
    '2s': "estuviste",
    '3s': "estuvo",
    '1p': "estuvimos",
    '2p': "estuvieron/estuvisteis",
    '3p': "estuvieron"
}

ESTAR_SUBJUNTIVO = {
    '1s': "estuviera",
    '2s': "estuvieras",
    '3s': "estuviera",
    '1p': "estuviéramos",
    '2p': "estuvieran/estuvierais",
    '3p': "estuvieran"
}

HABER = {
    '1s': "he",
    '2s': "has",
    '3s': "ha",
    '1p': "hemos",
    '2p': "han/habeis",
    '3p': "han"
}

DEJAR = {
    '1s': "dejara",
    '2s': "dejaras",
    '3s': "dejara",
    '1p': "dejáramos",
    '2p': "dejaran/dejarais",
    '3p': "dejaran"
}


def set_spanish_locale():
    spanish_locales = ['es_ES.UTF-8', 'es_CL.UTF-8', 'es_MX.UTF-8', 'es.UTF-8', '']
    for loc in spanish_locales:
        try:
            return locale.setlocale(locale.LC_ALL, loc)
        except locale.Error:
            continue
    return locale.setlocale(locale.LC_ALL, '')


def limpiar_consola():
    print("\n" * 100)


def mensaje_reinicio() -> None:
    print("\nNo es posible identificar el aktionsart de la cláusula con estos parámetros.")
    print("Por favor, revisa con cuidado tus respuestas a las preguntas.")
    #print("\nEl programa se reiniciará.")


def peticion(prompt: str) -> str:
    import sys
    readline.set_startup_hook(lambda: readline.insert_text(""))
    try:
        # Si el prompt es largo o tiene saltos de línea, imprímelo antes
        if "\n" in prompt or len(prompt) > 60:
            # end="" para que el cursor quede al final del texto
            print(prompt, end="", flush=True)
            user = input().strip()   # prompt corto y de una sola línea
        else:
            user = input(prompt).strip()
        return user.encode('utf-8').decode('utf-8')
    finally:
        readline.set_startup_hook()
        

def respuesta_si_no(pregunta: str) -> bool:
    while True:
        try:
            respuesta = peticion(pregunta).lower()
            if respuesta in Respuesta.SI.value:
                return True
            elif respuesta in Respuesta.NO.value:
                return False
            print("\nPor favor, entrega una respuesta válida: «sí (s)» o «no (n)».")
        except Exception as e:
            logging.error(f"Error al obtener respuesta: {e}")


def pedir_respuesta_multiple(pregunta: str, opciones: Sequence[Union[str, Sequence[str]]], prompt: str) -> str:
    while True:
        try:
            respuesta = peticion(f"{pregunta} {prompt}").lower()
            for opcion in opciones:
                if isinstance(opcion, Sequence) and not isinstance(opcion, str):
                    if respuesta in opcion:
                        return opcion[0]
                elif respuesta == opcion:
                    return opcion
            print("\nPor favor, escribe una respuesta válida.")
        except Exception as e:
            logging.error(f"Error al obtener respuesta: {e}")


def obtener_info_clausula(oracion: str, datos_clausula: DatosClause) -> DatosClause:
    datos_clausula.infinitivo = peticion(f"\nEscribe el INFINITIVO del verbo en «{oracion}», incluyendo los clíticos que haya (ejs: «derretirse», «decirle»): ")
    datos_clausula.gerundio = peticion(f"Escribe el GERUNDIO del verbo en «{oracion}», sin clíticos (ej: «derritiendo»): ")
    datos_clausula.participio = peticion(f"Escribe el PARTICIPIO (masculino singular) del verbo en «{oracion}» (ej: «derretido»): ")
    sujeto_input = peticion(f"Escribe todo lo que hay ANTES del verbo en «{oracion}», incluyendo los clíticos (0 si no hay nada): ")
    datos_clausula.sujeto = "" if sujeto_input == "0" else sujeto_input
    complementos_input = peticion(f"Escribe todo lo que hay DESPUÉS del verbo en «{oracion}» (0 si no hay nada): ")
    datos_clausula.complementos = "" if complementos_input == "0" else complementos_input
    persona_numero_pregunta = "Escribe la persona y número del verbo"
    persona_numero_prompt = "(1s/2s/3s/1p/2p/3p): "
    opciones_persona_numero: List[str] = ['1s', '2s', '3s', '1p', '2p', '3p']
    datos_clausula.persona_numero = pedir_respuesta_multiple(persona_numero_pregunta, opciones_persona_numero, persona_numero_prompt)
    datos_clausula.rasgos_obtenidos = True
    return datos_clausula

def construir_perif_gerundio(tiempo: str, datos_clausula: DatosClause) -> str:
    forma_estar = ESTAR_PRETERITO[datos_clausula.persona_numero] if tiempo == 'preterito' else ESTAR[datos_clausula.persona_numero]
    return " ".join(parte for parte in [datos_clausula.sujeto, f"{forma_estar} {datos_clausula.gerundio}", datos_clausula.complementos] if parte)

def construir_perif_gerundio_subj(datos_clausula: DatosClause) -> str:
    forma_estar = ESTAR_SUBJUNTIVO[datos_clausula.persona_numero]
    return " ".join(parte for parte in [datos_clausula.sujeto, f"{forma_estar} {datos_clausula.gerundio}", datos_clausula.complementos] if parte)

def construir_perif_participio(datos_clausula: DatosClause) -> str:
    forma_haber = HABER[datos_clausula.persona_numero]
    return " ".join(parte for parte in [datos_clausula.sujeto, f"{forma_haber} {datos_clausula.participio}", datos_clausula.complementos] if parte)

def construir_perif_infinitivo(datos_clausula: DatosClause) -> str:
    forma_dejar = DEJAR[datos_clausula.persona_numero]
    return " ".join(parte for parte in [f"{forma_dejar} de {datos_clausula.infinitivo}", datos_clausula.complementos] if parte)


def determinar_subtipo(pred_es: RasgosPred) -> Optional[str]:
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
        

#Pruebas de Aktionsart en funciones específicas
def prueba_causatividad(oracion: str) -> bool:
    print("\nPRUEBA DE CAUSATIVIDAD")
    print(f"\nIntenta reformular «{oracion}» siguiendo estos modelos: ")
    print("• El gato rompió el jarrón → El gato HIZO QUE el jarrón se rompiera")
    print("• Ana le dio un libro a Pepe → Ana HIZO QUE Pepe tuviera un libro")
    reformulacion = peticion("\nEscribe tu reformulación (o «0» si no es posible): ")
    if reformulacion == '0' or not reformulacion.strip():
        return False
    print("\nConsidera lo siguiente:")
    print(f"• «{reformulacion[0].upper() + reformulacion[1:]}» debe mantener el significado de «{oracion}».")
    print(f"• «{reformulacion[0].upper() + reformulacion[1:]}» no debe añadir nuevos argumentos ni repetir otros ya existentes en «{oracion}».")
    print(f"• El argumento expresado en el complemento directo de «{oracion}» debe sufrir un cambio de estado en «{reformulacion}».")
    print("• No debe tratarse de expresiones de consumo («comer una manzana») o creación («escribir un cuento»).")
    return respuesta_si_no(f"\n¿«{reformulacion[0].upper() + reformulacion[1:]}» cumple con estos criterios? (s/n): ")

def obtener_evento_basico() -> str:
    while True:
        evento = peticion("\nEscribe el evento o estado resultante sin la causa (ejs: «el jarrón se rompió», «Pepe tiene un libro»).\nSi no puedes pensar en ninguno, escribe «0»: ")
        if evento == "0" or evento.strip():
            return evento
        print("\nPor favor, ingresa una oración válida o «0» para cancelar.")

def prueba_estatividad(oracion: str) -> bool:
    print("\nPRUEBA DE ESTATIVIDAD")
    return not respuesta_si_no(
        f"\nObserva el siguiente diálogo:"
        f"\n—¿Qué pasó hace un rato / ayer / el mes pasado?"
        f"\n—{oracion[0].upper() + oracion[1:]}."
        f"\n\n¿Te parece que «{oracion}» es una buena respuesta a la pregunta? (con cualquiera de las opciones) (s/n): ")

def prueba_dinamicidad(datos_clausula: DatosClause) -> bool:
    perifrasis_gerundio = construir_perif_gerundio('presente', datos_clausula)
    print("\nPRUEBA DE DINAMICIDAD")
    return respuesta_si_no(
        f"\nObserva esta expresión: «{perifrasis_gerundio[0].upper() + perifrasis_gerundio[1:]} enérgicamente / con fuerza / con ganas»."
        f"\n¿Esta expresión es compatible con alguna de las opciones? (s/n): ")

def prueba_duratividad(datos_clausula: DatosClause) -> bool:
    perifrasis_gerundio = construir_perif_gerundio('preterito', datos_clausula)
    print("\nPRUEBA DE PUNTUALIDAD")
    return respuesta_si_no(
        f"\nObserva esta expresión: «{perifrasis_gerundio[0].upper() + perifrasis_gerundio[1:]} durante una hora / un mes»."
        f"\n¿Es esta una expresión posible? (sin que el evento tome una interpretación iterativa o de inminencia) (s/n): ")

def prueba_telicidad(datos_clausula: DatosClause) -> bool:
    perifrasis_gerundio = construir_perif_gerundio_subj(datos_clausula)
    perifrasis_participio = construir_perif_participio(datos_clausula)
    perifrasis_infinitivo = construir_perif_infinitivo(datos_clausula)
    print("\nPRUEBA DE TELICIDAD")
    pregunta = (f"\nImagina que {perifrasis_gerundio} y de pronto {perifrasis_infinitivo}."
                f"\n¿Se podría decir que «{perifrasis_participio}»? (s/n): ")
    return not respuesta_si_no(pregunta)
    

def obtener_rasgos_akt(oracion: str, datos_clausula: DatosClause) -> Union[RasgosPred, None]:
    pred_es = RasgosPred()
    datos_clausula.rasgos_obtenidos = False

    respuesta_causatividad = prueba_causatividad(oracion)
    if respuesta_causatividad:
        evento_basico = obtener_evento_basico()
        if evento_basico == "0":
            pred_es.causativo = False
            print("\nEl predicado es [-causativo]")
        else:
            pred_es.causativo = True
            print("\nEl predicado es [+causativo]")
            oracion = evento_basico
    else:
        pred_es.causativo = False
        print("\nEl predicado es [-causativo]")

    time.sleep(0.5)

    pred_es.estativo = prueba_estatividad(oracion)
    print(f"\nEl predicado es [{'+estativo' if pred_es.estativo else '-estativo'}]")
    time.sleep(0.5)

    if not pred_es.estativo:
        obtener_info_clausula(oracion, datos_clausula)
        
        pred_es.puntual = not prueba_duratividad(datos_clausula)
        print(f"\nEl predicado es [{'+puntual' if pred_es.puntual else '-puntual'}]")
        time.sleep(0.5)

        pred_es.telico = prueba_telicidad(datos_clausula)
        print(f"\nEl predicado es [{'+télico' if pred_es.telico else '-télico'}]")
        time.sleep(0.5)

        pred_es.dinamico = prueba_dinamicidad(datos_clausula)
        print(f"\nEl predicado es [{'+dinámico' if pred_es.dinamico else '-dinámico'}]")
        time.sleep(0.5)

    return pred_es


def mostrar_resultado(oracion_original: str, aktionsart: Aktionsart, pred_es: RasgosPred) -> None:
    print("\nRESULTADO")
    print(f"\nEl aktionsart del predicado de «{oracion_original}» es {aktionsart.value.upper()}.")

    akt_estado = aktionsart in [Aktionsart.ESTADO, Aktionsart.ESTADO_CAUSATIVO]

    rasgos_str = [
        f"[{'+causativo' if pred_es.causativo else '-causativo'}]",
        f"[{'+estativo' if pred_es.estativo else '-estativo'}]",
        f"[{'+puntual' if not akt_estado and pred_es.puntual else '-puntual'}]",
        f"[{'+télico' if not akt_estado and pred_es.telico else '-télico'}]",
    ]

    if akt_estado:
        rasgos_str.append("[-dinámico]")
        es_dinamico = False
    else:
        rasgos_str.append(f"[{'+dinámico' if pred_es.dinamico else '-dinámico'}]")
        es_dinamico = pred_es.dinamico

    print("\nEste predicado se clasifica así porque tiene los siguientes rasgos:")
    print(' '.join(rasgos_str))

    if respuesta_si_no("\n¿Quieres obtener la estructura lógica de esta cláusula? (s/n): "):
        print("\nEjecutando la opción elegida...")
        time.sleep(1)
        cargar_ls(aktionsart, oracion_original, es_dinamico)


def cargar_ls(aktionsart: Aktionsart, oracion_original: str, es_dinamico: bool) -> None:
    try:
        dinamico_str = "dinamico" if es_dinamico else "no_dinamico"
        cmd = [sys.executable, "-u", "ls.py", aktionsart.value, oracion_original, dinamico_str]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar ls.py: {e}")
    except FileNotFoundError:
        print("No se encontró el archivo ls.py en el directorio actual.")


def main() -> None:
    set_spanish_locale()
    limpiar_consola()
    print("\nEste programa te ayudará a identificar el aktionsart")
    print("del predicado principal en una cláusula.")

    while True:
        try:           
            oracion_original = peticion(
                "\nPor favor, escribe una cláusula con el verbo que quieres probar"
                "\nconjugado en pretérito (ej: «Pedro corrió hasta su casa»)."
                "\nSi suena muy extraña, escríbela en presente (ej: «María sabe inglés»)."
                "\n\nCláusula: "
            )

            if not oracion_original:
                print("\nNo has escrito ninguna cláusula.")
                continue

            oracion = oracion_original
            datos_clausula = DatosClause()

            pred_es = obtener_rasgos_akt(oracion, datos_clausula)
            if pred_es is None:
                continue
            aktionsart = determinar_aktionsart(pred_es)
            if aktionsart is None:
                mensaje_reinicio()
                continue
            mostrar_resultado(oracion_original, aktionsart, pred_es)

            if not respuesta_si_no("\n¿Quieres identificar el aktionsart de otro predicado? (s/n): "):
                time.sleep(1)
                return
            else:
                time.sleep(0.5)
                limpiar_consola()

        except Exception as e:
            logging.error(f"\nSe produjo un error inesperado: {e}")
            print("\nSe produjo un error. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    main()