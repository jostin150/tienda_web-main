
from typing import List, Optional
from models import User, Category, Product, Cart, Order

# ============================
# ESTADO GLOBAL (en memoria)
# ============================
usuarios: dict = User._users_by_email
categorias: List[Category] = []
productos: List[Product] = []
ordenes: List[Order] = []

usuario_actual: User | None = None
carrito_actual: Cart | None = None


# ============================
# SEED: datos de ejemplo
# ============================
def cargar_datos_ejemplo():
    cat = Category("Ropa", "ropa", "https://img.com/ropa.jpg")
    categorias.append(cat)
    productos.extend([
        Product("Camiseta Negra", 10, 50000, "M", "Negro", cat.id, "https://img.com/1.jpg"),
        Product("Gorra Azul", 5, 80000, "Única", "Azul", cat.id, "https://img.com/2.jpg"),
        Product("Jean Clásico", 8, 120000, "32", "Azul", cat.id, "https://img.com/3.jpg"),
    ])
    try:
        User.registrarse("Demo", "demo@demo.com", "1234", "3000000000")
    except ValueError:
        pass

