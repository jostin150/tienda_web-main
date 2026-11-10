from config import IVA_DEFAULT, ENVIO_BASE, ENVIO_GRATIS_DESDE
from enums import OrderStatus
import uuid

class OrderItem:
    def __init__(self, product, quantity, size=None, color=None, iva_rate=IVA_DEFAULT):
        self.product = product
        self.product_id = product.id
        self.name = product.name
        self.quantity = quantity
        self.size = size or product.size
        self.color = color or product.color
        self.unit_price = product.price
        self.iva_rate = iva_rate

    def subtotal(self):
        return self.unit_price * self.quantity

    def taxes(self):
        return self.subtotal() * self.iva_rate

    def total(self):
        return self.subtotal() + self.taxes()


class Order:
    def __init__(self, payment_method, user_id, address_id, products,
                 order_status=OrderStatus.PENDIENTE):
        self.id = str(uuid.uuid4())
        self.payment_method = payment_method
        self.user_id = user_id
        self.order_status = order_status
        self.address_id = address_id
        self.products = products
        self.shipping_cost = 0.0
        self.total = self.calcular_total()

    def subtotal(self):
        return sum(i.subtotal() for i in self.products)

    def taxes(self):
        return sum(i.taxes() for i in self.products)

    def calcular_envio(self):
        self.shipping_cost = 0.0 if self.subtotal() >= ENVIO_GRATIS_DESDE else ENVIO_BASE
        self.total = self.calcular_total()
        return self.shipping_cost

    def calcular_total(self):
        return self.subtotal() + self.taxes() + self.shipping_cost

    def confirmar_pago(self):
        if self.order_status != OrderStatus.PENDIENTE:
            raise ValueError("Solo se paga una orden pendiente")
        for i in self.products:
            i.product.reducir_stock(i.quantity)
        self.order_status = OrderStatus.PAGADO

    def actualizar_estado(self, nuevo):
        trans = {
            OrderStatus.PENDIENTE: {OrderStatus.PAGADO, OrderStatus.CANCELADO},
            OrderStatus.PAGADO: {OrderStatus.ENVIADO, OrderStatus.CANCELADO},
            OrderStatus.ENVIADO: {OrderStatus.ENTREGADO},
            OrderStatus.ENTREGADO: set(),
            OrderStatus.CANCELADO: set(),
        }
        if nuevo not in trans[self.order_status]:
            raise ValueError(f"No puedes pasar de {self.order_status.value} a {nuevo.value}")
        self.order_status = nuevo

