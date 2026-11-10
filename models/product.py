import uuid

class Product:
    def __init__(self, name, stock, price, size, color, category_id, image, id=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.stock = stock
        self.price = float(price)
        self.size = size
        self.color = color
        self.category_id = category_id
        self.image = image

    def hay_stock(self, c):
        return c > 0 and self.stock >= c

    def reducir_stock(self, c):
        if not self.hay_stock(c):
            raise ValueError(f"Stock insuficiente para {self.name}")
        self.stock -= c
