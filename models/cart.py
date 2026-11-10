from __future__ import annotations
from config import IVA_DEFAULT
from models.order import Order, OrderItem
from typing import List

class Cart:
    def __init__(self, user_id, iva_rate=IVA_DEFAULT):
        self.user_id = user_id
        self.items: List[CartItem] = []
        self.iva_rate = iva_rate

    def add(self, product, quantity=1):
        for item in self.items:
            if item.product_id == product.id:
                nueva = item.quantity + quantity
                if not product.hay_stock(nueva):
                    raise ValueError("Stock insuficiente")
                item.quantity = nueva
                return item
        item = CartItem(product, quantity, iva_rate=self.iva_rate)
        self.items.append(item)
        return item

    def remove(self, product_id):
        antes = len(self.items)
        self.items = [i for i in self.items if i.product_id != product_id]
        return len(self.items) < antes

    def subtotal(self):
        return sum(i.subtotal() for i in self.items)

    def taxes(self):
        return sum(i.taxes() for i in self.items)

    def total(self):
        return self.subtotal() + self.taxes()

    def vaciar(self):
        self.items.clear()

    def make_order(self, payment_method, address_id):
        if not self.items:
            raise ValueError("El carrito está vacío")
        for i in self.items:
            if not i.product.hay_stock(i.quantity):
                raise ValueError(f"Stock insuficiente para {i.product.name}")
        order = Order(payment_method, self.user_id, address_id,
                      [i.to_order_item() for i in self.items])
        self.vaciar()
        return order

class CartItem:
    def __init__(self, product, quantity, size=None, color=None, iva_rate=IVA_DEFAULT):
        if not product.hay_stock(quantity):
            raise ValueError(f"Sin stock para {product.name}")
        self.product = product
        self.product_id = product.id
        self.quantity = quantity
        self.size = size or product.size
        self.color = color or product.color
        self.iva_rate = iva_rate

    def subtotal(self):
        return self.product.price * self.quantity

    def taxes(self):
        return self.subtotal() * self.iva_rate

    def total(self):
        return self.subtotal() + self.taxes()

    def to_order_item(self):
        return OrderItem(self.product, self.quantity, self.size, self.color, self.iva_rate)
