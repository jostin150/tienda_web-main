from state.store import carrito_actual, ordenes, usuario_actual
from utils import limpiar, pausar, pedir, money
from enums import OrderStatus

def hacer_orden():
    if not usuario_actual.addresses:
        print("\n  ⚠ Necesitas al menos una dirección de envío")
        pausar()
        return

    print("\n  Direcciones disponibles:")
    for i, a in enumerate(usuario_actual.addresses, 1):
        print(f"    {i}. {a.address}, {a.city} ({a.tag or 'sin etiqueta'})")
    idx = pedir("  Elegir dirección: ", int)
    if not (1 <= idx <= len(usuario_actual.addresses)):
        print("\n  ✗ Dirección inválida"); pausar(); return
    addr = usuario_actual.addresses[idx - 1]

    print("\n  Métodos de pago: tarjeta / pse / efectivo / nequi")
    pm = pedir("  Método: ")

    try:
        order = carrito_actual.make_order(pm, addr.id)
        order.calcular_envio()
        ordenes.append(order)
        print(f"\n  ✓ Orden creada")
        print(f"    Subtotal: {money(order.subtotal())}")
        print(f"    IVA:      {money(order.taxes())}")
        print(f"    Envío:    {money(order.shipping_cost)}")
        print(f"    Total:    {money(order.total)}")
        print(f"    Estado:   {order.order_status.value}")
    except ValueError as e:
        print(f"\n  ✗ {e}")
    pausar()


def vista_ordenes():
    limpiar()
    print("=== MIS ÓRDENES ===\n")
    mis = [o for o in ordenes if o.user_id == usuario_actual.id]
    if not mis:
        print("  (No tienes órdenes)")
        pausar()
        return

    for i, o in enumerate(mis, 1):
        print(f"  {i}. [{o.order_status.value}] Total: {money(o.total)} "
              f"({len(o.products)} productos)")
    print("\n  Elige una orden para gestionarla (o ENTER para volver):")
    op = input("  Orden: ").strip()
    if not op.isdigit():
        return
    idx = int(op) - 1
    if 0 <= idx < len(mis):
        detalle_orden(mis[idx])


def detalle_orden(o):
    limpiar()
    print("=== DETALLE DE ORDEN ===\n")
    for item in o.products:
        print(f"  - {item.name} x{item.quantity} = {money(item.subtotal())}")
    print(f"\n  Subtotal: {money(o.subtotal())}")
    print(f"  IVA:      {money(o.taxes())}")
    print(f"  Envío:    {money(o.shipping_cost)}")
    print(f"  Total:    {money(o.total)}")
    print(f"  Estado:   {o.order_status.value}")
    print(f"  Pago:     {o.payment_method}")
    print("\n  Acciones:")
    print("  1. Confirmar pago")
    print("  2. Confirmar envío")
    print("  3. Marcar entregado")
    print("  4. Cancelar")
    print("  0. Volver")
    op = input("  Opción: ").strip()
    try:
        if op == "1":
            o.confirmar_pago()
        elif op == "2":
            o.actualizar_estado(OrderStatus.ENVIADO)
        elif op == "3":
            o.actualizar_estado(OrderStatus.ENTREGADO)
        elif op == "4":
            o.actualizar_estado(OrderStatus.CANCELADO)
        else:
            return
        print(f"\n  ✓ Nuevo estado: {o.order_status.value}")
    except ValueError as e:
        print(f"\n  ✗ {e}")
    pausar()