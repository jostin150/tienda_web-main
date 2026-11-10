import pg8000.dbapi
from models.order import Order, OrderItem
from enums import OrderStatus
from models import Product, User, Address
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

#================
#Conectar a la base de datos
#================
def conectar():
    return pg8000.dbapi.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME,
    )

def consultar(sql, params=()):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, f)) for f in cur.fetchall()]
    finally:
        conn.close()

        from models import Product

def cargar_productos():
    filas = consultar(
        "SELECT id, nombre, stock, precio, talla, color, imagen FROM productos"
    )
    return [
        Product(f["nombre"], f["stock"], f["precio"], f["talla"],
                f["color"], None, f["imagen"], id=f["id"])
        for f in filas
    ]

def ejecutar(sql, params=()):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()

def guardar_stock(product_id, stock):
    ejecutar("UPDATE productos SET stock = %s WHERE id = %s ", (stock, product_id))

def cargar_usuarios():
    filas = consultar("SELECT id, nombre, email, password, telefono FROM usuarios")
    for f in filas:
        u = User(f["nombre"], f["email"], f["password"], f["telefono"])
        u.id = f["id"]
        User._users_by_email[u.email] = u

def guardar_usuario(u):
    ejecutar(
        "INSERT INTO Usuarios (id, nombre, email, password, telefono) "
        "VALUES (%s, %s, %s, %s, %s)",
        (u.id, u.name, u.email, u.password, u.phone)
    )

def actualizar_usuario(u):
    ejecutar(
        "UPDATE Usuarios SET nombre = %s, email = %s, password = %s, telefono = %s WHERE id = %s",
        (u.name, u.email, u.password, u.phone, u.id)
    )

def cargar_direcciones():
    filas = consultar(
        "SELECT id, user_id, direccion, ciudad, apartamento, etiqueta, "
        "referencia, receptor, telefono FROM direcciones"
    )
    usuarios = {u.id: u for u in User._users_by_email.values()}
    for f in filas:
        u = usuarios.get(f["user_id"])
        if not u:
            continue
        a = Address(f["user_id"], f["direccion"], f["ciudad"],
                    f["apartamento"], f["etiqueta"], f["referencia"],
                    f["receptor"], f["telefono"])
        a.id = f["id"]
        a.add_address(u)


def guardar_direccion(a):
    ejecutar(
        "INSERT INTO direcciones (id, user_id, direccion, ciudad, apartamento, "
        "etiqueta, referencia, receptor, telefono) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (a.id, a.user_id, a.address, a.city, a.apartment_number,
         a.tag, a.reference_place, a.receiver_name, a.phone_number),
    )


def borrar_direccion(address_id, user_id):
    ejecutar(
        "DELETE FROM direcciones WHERE id = %s AND user_id = %s",
        (address_id, user_id),
    )

def cargar_ordenes(productos):
    por_id = {p.id: p for p in productos}
    filas = consultar(
        "SELECT id, user_id, direccion_id, metodo_pago, estado, costo_envio "
        "FROM ordenes ORDER BY creada"
    )
    items = consultar(
        "SELECT orden_id, producto_id, nombre, cantidad, talla, color, "
        "precio_unitario, iva FROM orden_items ORDER BY id"
    )
    items_por_orden = {}
    for it in items:
        p = por_id.get(it["producto_id"])
        if not p:
            continue
        oi = OrderItem(p, it["cantidad"], it["talla"], it["color"], float(it["iva"]))
        oi.name = it["nombre"]
        oi.unit_price = float(it["precio_unitario"])
        items_por_orden.setdefault(it["orden_id"], []).append(oi)

    ordenes = []
    for f in filas:
        o = Order(f["metodo_pago"], f["user_id"], f["direccion_id"],
                  items_por_orden.get(f["id"], []), OrderStatus(f["estado"]))
        o.id = f["id"]
        o.shipping_cost = float(f["costo_envio"])
        o.total = o.calcular_total()
        ordenes.append(o)
    return ordenes


def guardar_orden(o):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ordenes (id, user_id, direccion_id, metodo_pago, "
            "estado, costo_envio, total) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (o.id, o.user_id, o.address_id, o.payment_method,
             o.order_status.value, o.shipping_cost, o.total),
        )
        for i in o.products:
            cur.execute(
                "INSERT INTO orden_items (orden_id, producto_id, nombre, cantidad, "
                "talla, color, precio_unitario, iva) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (o.id, i.product_id, i.name, i.quantity, i.size,
                 i.color, i.unit_price, i.iva_rate),
            )
        conn.commit()
    finally:
        conn.close()


def actualizar_estado_orden(o):
    ejecutar(
        "UPDATE ordenes SET estado = %s WHERE id = %s",
        (o.order_status.value, o.id),
    )

def guardar_producto(p):
    ejecutar(
        "INSERT INTO productos (id, nombre, stock, precio, talla, color, imagen) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (p.id, p.name, p.stock, p.price, p.size, p.color, p.image),
    )


def actualizar_producto(p):
    ejecutar(
        "UPDATE productos SET nombre = %s, stock = %s, precio = %s, talla = %s, "
        "color = %s, imagen = %s WHERE id = %s",
        (p.name, p.stock, p.price, p.size, p.color, p.image, p.id),
    )
