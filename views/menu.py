from state import store
from utils import limpiar, pausar
from .auth import vista_registro, vista_login, cerrar_sesion
from .user import vista_direcciones, vista_actualizar
from .products import vista_productos
from .cart import vista_carrito
from .order import vista_ordenes

def menu_principal():
    while True:
        limpiar()
        print("=" * 50)
        print("        🛒  TIENDA INTERACTIVA")
        print("=" * 50)
        if store.usuario_actual:
            print(f"  Sesión: {store.usuario_actual.name} <{store.usuario_actual.email}>")
        else:
            print("  Sesión: (invitado)")
        print("-" * 50)
        if store.usuario_actual:
            print("  3. Actualizar mis datos")
            print("  4. Mis direcciones")
            print("  5. Ver productos")
            print("  6. Mi carrito")
            print("  7. Mis órdenes")
            print("  8. Cerrar sesión")
        else:
            print("  1. Registrarse")
            print("  2. Iniciar sesión")
            print("  5. Ver productos")
        print("  0. Salir")
        print("=" * 50)

        op = input("  Elige una opción: ").strip()

        if op == "1" and not store.usuario_actual:
            vista_registro()
        elif op == "2" and not store.usuario_actual:
            vista_login()
        elif op == "3" and store.usuario_actual:
            vista_actualizar()
        elif op == "4" and store.usuario_actual:
            vista_direcciones()
        elif op == "5":
            vista_productos()
        elif op == "6" and store.usuario_actual:
            vista_carrito()
        elif op == "7" and store.usuario_actual:
            vista_ordenes()
        elif op == "8" and store.usuario_actual:
            cerrar_sesion()
        elif op == "0":
            print("\n  ¡Hasta luego!\n")
            break
        else:
            print("  ⚠ Opción inválida")
            pausar()