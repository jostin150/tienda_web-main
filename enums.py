# ============================
# ESTADOS DE PEDIDO
# ============================
from enum import Enum

class OrderStatus(Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"
