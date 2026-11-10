from state.store import carrito_actual, ordenes
from utils import limpiar, pausar, pedir, money
from .order import hacer_orden

def vista_carrito():
    limpiar()
    print("=== MI CARRITO ===\n")
    if not carrito_actual.items:
        print("  (Carrito vacío)")
        pausar()
        return

    for i, item in enumerate(carrito_actual.items, 1):
        print(f"  {i}. {item.product.name} x{item.quantity} "
              f"= {money(item.subtotal())}")

    print("\n  " + "-" * 40)
    print(f"  Subtotal: {money(carrito_actual.subtotal())}")
    print(f"  IVA:      {money(carrito_actual.taxes())}")
    print(f"  Total:    {money(carrito_actual.total())}")
    print("  " + "-" * 40)
    print("\n  1. Quitar producto")
    print("  2. Vaciar carrito")
    print("  3. Hacer orden")
    print("  0. Volver")
    op = input("  Opción: ").strip()

    if op == "1":
        idx = pedir("Número a quitar: ", int)
        if 1 <= idx <= len(carrito_actual.items):
            pid = carrito_actual.items[idx - 1].product_id
            carrito_actual.remove(pid)
            print("\n  ✓ Producto quitado")
        pausar()
    elif op == "2":
        carrito_actual.vaciar()
        print("\n  ✓ Carrito vacío")
        pausar()
    elif op == "3":
        hacer_orden()