from models import Address
from utils import limpiar, pedir, pausar
from state.store import usuario_actual

def vista_actualizar():
    limpiar()
    print("=== ACTUALIZAR DATOS ===")
    print("  (deja vacío para no cambiar)\n")
    name = input(f"Nombre [{usuario_actual.name}]: ").strip()
    email = input(f"Email [{usuario_actual.email}]: ").strip()
    phone = input(f"Teléfono [{usuario_actual.phone}]: ").strip()
    password = input("Nueva contraseña (opcional): ").strip()
    try:
        usuario_actual.actualizar_datos(
            name=name or None,
            email=email or None,
            phone=phone or None,
            password=password or None,
        )
        print("\n  ✓ Datos actualizados")
    except ValueError as e:
        print(f"\n  ✗ {e}")
    pausar()


def vista_direcciones():
    limpiar()
    print("=== MIS DIRECCIONES ===\n")
    if usuario_actual.addresses:
        for i, a in enumerate(usuario_actual.addresses, 1):
            print(f"  {i}. {a.address}, {a.city} ({a.tag or 'sin etiqueta'})")
    else:
        print("  (No tienes direcciones)")
    print("\n  1. Agregar dirección")
    print("  2. Eliminar dirección")
    print("  0. Volver")
    op = input("  Opción: ").strip()

    if op == "1":
        address = pedir("Dirección: ")
        city = pedir("Ciudad: ")
        apt = input("Apartamento (opcional): ").strip() or None
        tag = input("Etiqueta (Casa/Oficina, opcional): ").strip() or None
        ref = input("Punto de referencia (opcional): ").strip() or None
        recv = input(f"Nombre de quien recibe [{usuario_actual.name}]: ").strip() or usuario_actual.name
        phone = input(f"Teléfono [{usuario_actual.phone}]: ").strip() or usuario_actual.phone
        addr = Address(usuario_actual.id, address, city, apt, tag, ref, recv, phone)
        addr.add_address(usuario_actual)
        print("\n  ✓ Dirección agregada")
        pausar()
    elif op == "2":
        if not usuario_actual.addresses:
            print("  No hay direcciones"); pausar(); return
        idx = pedir("Número de dirección a eliminar: ", int)
        if 1 <= idx <= len(usuario_actual.addresses):
            usuario_actual.addresses.pop(idx - 1)
            print("\n  ✓ Eliminada")
        else:
            print("\n  ✗ Número inválido")
        pausar()