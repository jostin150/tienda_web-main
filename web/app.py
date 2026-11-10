import os
import sys
from functools import wraps

# Permite ejecutar `python web/app.py` desde la raíz del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

from models import User, Cart, Address, Product, Order
from enums import OrderStatus
from state import store
from state.store import cargar_datos_ejemplo
from utils import money
from config import ADMIN_EMAILS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-tienda-cambiar-en-produccion")
app.jinja_env.filters["money"] = money

#===========================
#IMPORT(Este carga los datos de la web a la base de datos)
#============================
cargar_datos_ejemplo()
from db import (cargar_productos, guardar_producto, actualizar_producto, guardar_stock, cargar_usuarios, guardar_usuario, actualizar_usuario, cargar_direcciones, guardar_direccion, borrar_direccion, cargar_ordenes, guardar_orden, actualizar_estado_orden)
store.productos = cargar_productos()
cargar_datos_ejemplo()
store.productos[:] = cargar_productos()
cargar_usuarios()
cargar_direcciones()
store.ordenes[:] = cargar_ordenes(store.productos)

# ============================|
# SESIÓN WEB
# ============================
# En consola hay un solo usuario (store.usuario_actual). En la web cada
# navegador tiene su propia sesión, así que se guarda el id del usuario
# en la cookie y un carrito por usuario.
carritos: dict = {}

METODOS_PAGO = ["tarjeta", "pse", "efectivo", "nequi"]


def usuario_actual():
    uid = session.get("user_id")
    if not uid:
        return None
    for u in store.usuarios.values():
        if u.id == uid:
            return u
    session.pop("user_id", None)
    return None


def carrito_actual():
    u = usuario_actual()
    if u.id not in carritos:
        carritos[u.id] = Cart(u.id)
    return carritos[u.id]


def buscar_producto(product_id):
    for p in store.productos:
        if p.id == product_id:
            return p
    abort(404)


def es_admin(u):
    return bool(u) and u.email in ADMIN_EMAILS


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not usuario_actual():
            flash("Inicia sesión para continuar", "error")
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


def admin_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        u = usuario_actual()
        if not u:
            flash("Inicia sesión para continuar", "error")
            return redirect(url_for("login"))
        if not es_admin(u):
            flash("Solo el administrador puede hacer eso", "error")
            return redirect(url_for("productos"))
        return vista(*args, **kwargs)
    return envoltura


def solo_invitado(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if usuario_actual():
            return redirect(url_for("inicio"))
        return vista(*args, **kwargs)
    return envoltura


@app.context_processor
def contexto_global():
    u = usuario_actual()
    items = len(carritos[u.id].items) if u and u.id in carritos else 0
    return {"usuario": u, "items_carrito": items, "es_admin": es_admin(u)}


# ============================
# INICIO / AUTH
# ============================
@app.route("/")
def inicio():
    if not usuario_actual():
        return redirect(url_for("login"))
    return render_template("inicio.html", productos=store.productos)


@app.route("/registro", methods=["GET", "POST"])
@solo_invitado
def registro():
    if request.method == "POST":
        f = request.form
        try:
            u = User.registrarse(f["name"], f["email"], f["password"], f["phone"])
            guardar_usuario(u)
            flash(f"Usuario '{f['name']}' registrado con éxito. Ya puedes iniciar sesión.", "ok")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
@solo_invitado
def login():
    if request.method == "POST":
        try:
            u = User.ingresar(request.form["email"], request.form["password"])
            session["user_id"] = u.id
            flash(f"Bienvenido/a, {u.name}", "ok")
            return redirect(url_for("inicio"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("Sesión cerrada", "ok")
    return redirect(url_for("inicio"))


# ============================
# USUARIO
# ============================
@app.route("/mis-datos", methods=["GET", "POST"])
@login_requerido
def actualizar():
    u = usuario_actual()
    if request.method == "POST":
        f = request.form
        try:
            u.actualizar_datos(
                name=f["name"].strip() or None,
                email=f["email"].strip() or None,
                phone=f["phone"].strip() or None,
                password=f["password"].strip() or None,
            )
            actualizar_usuario(u)
            
            flash("Datos actualizados", "ok")
            return redirect(url_for("actualizar"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("actualizar.html")


@app.route("/direcciones", methods=["GET", "POST"])
@login_requerido
def direcciones():
    u = usuario_actual()
    if request.method == "POST":
        f = request.form
        addr = Address(
            u.id, f["address"], f["city"],
            f["apartment_number"].strip() or None,
            f["tag"].strip() or None,
            f["reference_place"].strip() or None,
            f["receiver_name"].strip() or u.name,
            f["phone_number"].strip() or u.phone,
        )
        addr.add_address(u)
        guardar_direccion(addr)
        flash("Dirección agregada", "ok")
        return redirect(url_for("direcciones"))
    return render_template("direcciones.html")


@app.route("/direcciones/<address_id>/eliminar", methods=["POST"])
@login_requerido
def eliminar_direccion(address_id):
    u = usuario_actual()
    u.addresses = [a for a in u.addresses if a.id != address_id]
    borrar_direccion(address_id, u.id)
    flash("Dirección eliminada", "ok")
    return redirect(url_for("direcciones"))


# ============================
# PRODUCTOS
# ============================
@app.route("/productos")
def productos():
    return render_template("productos.html", productos=store.productos)

@app.route("/productos/nuevo", methods=["GET", "POST"])
@admin_requerido
def nuevo_producto():
    if request.method == "POST":
        f = request.form
        try:
            nombre = f["nombre"].strip()
            if not nombre:
                raise ValueError("El nombre es obligatorio")
            try:
                stock = int(f["stock"])
                precio = float(f["precio"])
            except ValueError:
                raise ValueError("Stock y precio deben ser números")
            if stock < 0 or precio <= 0:
                raise ValueError("El stock no puede ser negativo y el precio debe ser mayor a 0")
            p = Product(nombre, stock, precio,
                        f["talla"].strip(), f["color"].strip(),
                        None, f["imagen"].strip())
            guardar_producto(p)
            store.productos.append(p)
            flash(f"Producto '{p.name}' agregado", "ok")
            return redirect(url_for("productos"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("nuevo_producto.html")


@app.route("/productos/<product_id>")
def detalle_producto(product_id):
    return render_template("producto.html", p=buscar_producto(product_id))


@app.route("/productos/<product_id>/agregar", methods=["POST"])
@login_requerido
def agregar_carrito(product_id):
    p = buscar_producto(product_id)
    try:
        cant = int(request.form.get("cantidad") or 1)
        carrito_actual().add(p, cant)
        flash(f"'{p.name}' x{cant} agregado al carrito", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(request.referrer or url_for("detalle_producto", product_id=p.id))


# ============================
# CARRITO
# ============================
@app.route("/carrito")
@login_requerido
def carrito():
    return render_template("carrito.html", carrito=carrito_actual(), metodos=METODOS_PAGO)


@app.route("/carrito/<product_id>/quitar", methods=["POST"])
@login_requerido
def quitar_carrito(product_id):
    carrito_actual().remove(product_id)
    flash("Producto quitado", "ok")
    return redirect(url_for("carrito"))


@app.route("/carrito/vaciar", methods=["POST"])
@login_requerido
def vaciar_carrito():
    carrito_actual().vaciar()
    flash("Carrito vacío", "ok")
    return redirect(url_for("carrito"))


@app.route("/carrito/ordenar", methods=["POST"])
@login_requerido
def hacer_orden():
    u = usuario_actual()
    address_id = request.form.get("address_id")
    pm = request.form.get("payment_method")
    if not any(a.id == address_id for a in u.addresses):
        flash("Dirección inválida", "error")
        return redirect(url_for("carrito"))
    if pm not in METODOS_PAGO:
        flash("Método de pago inválido", "error")
        return redirect(url_for("carrito"))
    try:
        order = carrito_actual().make_order(pm, address_id)
        order.calcular_envio()
        store.ordenes.append(order)
        guardar_orden(order)
        flash("Orden creada", "ok")
        return redirect(url_for("detalle_orden", order_id=order.id))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("carrito"))


# ============================
# ÓRDENES
# ============================
def buscar_orden(order_id):
    u = usuario_actual()
    for o in store.ordenes:
        if o.id == order_id and (o.user_id == u.id or es_admin(u)):
            return o
    abort(404)


@app.route("/ordenes")
@login_requerido
def ordenes():
    u = usuario_actual()
    mis = [o for o in store.ordenes if o.user_id == u.id]
    return render_template("ordenes.html", ordenes=mis)


def aplicar_accion(o, accion):
    """Cambia el estado de una orden. Solo la usa el administrador."""
    if accion == "pagar":
        o.confirmar_pago()
        for item in o.products:
            guardar_stock(item.product.id, item.product.stock)
    elif accion == "enviar":
        o.actualizar_estado(OrderStatus.ENVIADO)
    elif accion == "entregar":
        o.actualizar_estado(OrderStatus.ENTREGADO)
    elif accion == "cancelar":
        estaba_pagada = o.order_status == OrderStatus.PAGADO
        o.actualizar_estado(OrderStatus.CANCELADO)
        if estaba_pagada:
            for item in o.products:
                item.product.stock += item.quantity
                guardar_stock(item.product.id, item.product.stock)
    else:
        raise ValueError("Acción no válida")
    actualizar_estado_orden(o)


# Acciones que el admin puede aplicar según el estado actual de la orden
ACCIONES_POR_ESTADO = {
    OrderStatus.PENDIENTE: [("pagar", "Confirmar pago"), ("cancelar", "Cancelar")],
    OrderStatus.PAGADO: [("enviar", "Marcar enviado"), ("cancelar", "Cancelar")],
    OrderStatus.ENVIADO: [("entregar", "Marcar entregado")],
    OrderStatus.ENTREGADO: [],
    OrderStatus.CANCELADO: [],
}


@app.route("/ordenes/<order_id>", methods=["GET", "POST"])
@login_requerido
def detalle_orden(order_id):
    o = buscar_orden(order_id)
    if request.method == "POST":
        if not es_admin(usuario_actual()):
            flash("Solo el administrador puede cambiar el estado de los pedidos", "error")
            return redirect(url_for("detalle_orden", order_id=o.id))
        try:
            aplicar_accion(o, request.form.get("accion"))
            flash(f"Nuevo estado: {o.order_status.value}", "ok")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("detalle_orden", order_id=o.id))
    todos = list(store.usuarios.values())
    direccion = next((a for usr in todos for a in usr.addresses if a.id == o.address_id), None)
    cliente = next((usr for usr in todos if usr.id == o.user_id), None)
    return render_template("orden.html", o=o, direccion=direccion, cliente=cliente)


# ============================
# ADMINISTRACIÓN
# ============================
@app.route("/admin")
@admin_requerido
def admin():
    clientes = {u.id: u for u in store.usuarios.values()}
    return render_template("admin.html", productos=store.productos,
                           ordenes=list(reversed(store.ordenes)), clientes=clientes,
                           acciones=ACCIONES_POR_ESTADO)


@app.route("/admin/productos/<product_id>/stock", methods=["POST"])
@admin_requerido
def agregar_stock(product_id):
    p = buscar_producto(product_id)
    try:
        cantidad = int(request.form.get("cantidad", ""))
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash("La cantidad debe ser un número entero mayor a 0", "error")
        return redirect(url_for("admin"))
    p.stock += cantidad
    guardar_stock(p.id, p.stock)
    flash(f"Stock de '{p.name}': +{cantidad} (ahora {p.stock})", "ok")
    return redirect(url_for("admin"))


@app.route("/admin/ordenes/<order_id>/estado", methods=["POST"])
@admin_requerido
def admin_cambiar_estado(order_id):
    o = buscar_orden(order_id)
    try:
        aplicar_accion(o, request.form.get("accion"))
        flash(f"Pedido actualizado: {o.order_status.value}", "ok")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin"))


@app.route("/admin/productos/<product_id>/editar", methods=["GET", "POST"])
@admin_requerido
def editar_producto(product_id):
    p = buscar_producto(product_id)
    if request.method == "POST":
        f = request.form
        try:
            nombre = f["nombre"].strip()
            if not nombre:
                raise ValueError("El nombre es obligatorio")
            try:
                stock = int(f["stock"])
                precio = float(f["precio"])
            except ValueError:
                raise ValueError("Stock y precio deben ser números")
            if stock < 0 or precio <= 0:
                raise ValueError("El stock no puede ser negativo y el precio debe ser mayor a 0")
            p.name = nombre
            p.stock = stock
            p.price = precio
            p.size = f["talla"].strip()
            p.color = f["color"].strip()
            p.image = f["imagen"].strip()
            actualizar_producto(p)
            flash(f"Producto '{p.name}' actualizado", "ok")
            return redirect(url_for("admin"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("editar_producto.html", p=p)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))