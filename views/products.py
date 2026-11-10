from state.store import productos, usuario_actual, carrito_actual
from utils import limpiar, pausar, pedir, money

def mostrar_productos():
    if not productos:
        print("  (No hay productos)")
        return
    print(f"\n  {'#':<4}{'Producto':<20}{'Precio':<12}{'Stock':<8}{'Talla':<8}{'Color'}")
    print("  " + "-" * 60)
    for idx, p in enumerate(productos, 1):
        print(f"  {idx:<4}{p.name:<20}{money(p.price):<12}{p.stock:<8}{p.size:<8}{p.color}")


def vista_productos():
    limpiar()
    print("=== PRODUCTOS ===\n")
    mostrar_productos()
    print("\n  Escribe el número de un producto para ver detalle,")
    print("  o ENTER para volver.")
    op = input("  Producto: ").strip()
    if op.isdigit():
        idx = int(op) - 1
        if 0 <= idx < len(productos):
            detalle_producto(productos[idx])


def detalle_producto(p):
    limpiar()
    print("=== DETALLE DE PRODUCTO ===\n")
    print(f"  Nombre: {p.name}")
    print(f"  Precio: {money(p.price)}")
    print(f"  Stock:  {p.stock}")
    print(f"  Talla:  {p.size}")
    print(f"  Color:  {p.color}")
    print(f"  Imagen: {p.image}")
    if not usuario_actual:
        print("\n  ⚠ Inicia sesión para agregar al carrito")
        pausar()
        return
    print("\n  1. Agregar al carrito")
    print("  0. Volver")
    if input("  Opción: ").strip() == "1":
        try:
            cant = pedir("Cantidad: ", int, default=1)
            carrito_actual.add(p, cant)
            print(f"\n  ✓ '{p.name}' x{cant} agregado al carrito")
        except ValueError as e:
            print(f"\n  ✗ {e}")
        pausar()
