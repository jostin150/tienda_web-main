import os

# ============================
# UTILIDADES
# ============================
def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def pedir(msg, tipo=str, default=None):
    """Pide un dato, valida el tipo y permite valor por defecto."""
    while True:
        valor = input(msg).strip()
        if not valor and default is not None:
            return default
        try:
            return tipo(valor)
        except ValueError:
            print(f"  ⚠ Valor inválido, intenta de nuevo.")


def pedir_opcion(msg, opciones_validas):
    while True:
        valor = input(msg).strip()
        if valor in opciones_validas:
            return valor
        print(f"  ⚠ Opción inválida. Válidas: {', '.join(opciones_validas)}")


def pausar():
    input("\nPresiona ENTER para continuar...")