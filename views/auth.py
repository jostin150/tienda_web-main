from models import User, Cart
from utils import limpiar, pedir, pausar
from state import store

def vista_registro():
   limpiar()
   print("=== REGISTRO ===\n")
   name = pedir("Nombre: ")
   email = pedir("Email: ")
   password = pedir("Contraseña: ")
   phone = pedir("Teléfono: ")
   try:
      User.registrarse(name, email, password, phone)
      print(f"\n  ✓ Usuario '{name}' registrado con éxito")
   except ValueError as e:
      print(f"\n  ✗ Error: {e}")
   pausar()


def vista_login():
   limpiar()
   print("=== INICIAR SESIÓN ===\n")
   email = pedir("Email: ")
   password = pedir("Contraseña: ")
   try:
      store.usuario_actual = User.ingresar(email, password)
      store.carrito_actual = Cart(store.usuario_actual.id)
      print(f"\n  ✓ Bienvenido/a, {store.usuario_actual.name}")
   except ValueError as e:
      print(f"\n  ✗ {e}")
   pausar()

def cerrar_sesion():
   store.usuario_actual = None
   store.carrito_actual = None
   print("\n  ✓ Sesión cerrada")
   pausar()