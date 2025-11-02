import subprocess
import time


def limpiar_consola():
    print("\n" * 100)


def ejecutar_programa(programa):
    try:
        print("\nEjecutando la opción elegida...")
        time.sleep(1)
        subprocess.run(["python3", programa], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {programa}: {e}")
    except FileNotFoundError:
        print(f"No se encontró el archivo {programa} en el directorio actual.")


def mostrar_menu() -> str:
    mensaje_bienvenida = """
Bienvenido a este asistente para la detección de aktionsart y la formalización de estructuras
lógicas básicas en el marco de la Gramática de Papel y Referencia (RRG).

¿Qué quieres hacer?:
"""
    opciones = [
        "1. Identificar el aktionsart de un predicado (y, opcionalmente, obtener su estructura lógica)",
        "2. Obtener la estructura lógica de una cláusula (si ya conoces el aktionsart de su predicado)",
        "3. Salir"
    ]

    print(mensaje_bienvenida)
    for opcion in opciones:
        print(opcion)

    return input("\nPor favor, selecciona una opción (1-3): ")


def main():
    while True:
        limpiar_consola()
        opcion = mostrar_menu()
        if opcion == "1":
            ejecutar_programa("aktionsart.py")
        elif opcion == "2":
            ejecutar_programa("ls.py")
        elif opcion == "3":
            print("\nGracias por usar este asistente. ¡Hasta luego!")
            break
        else:
            print("\nOpción no válida. Por favor, intenta de nuevo.")
            time.sleep(1)

if __name__ == "__main__":
    main()