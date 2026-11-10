import os
from __future__ import annotations
from typing import List
from datetime import datetime
from config import IVA_DEFAULT, ENVIO_BASE, ENVIO_GRATIS_DESDE
from enums import OrderStatus
from utils import *
from models import User, Category, Product, Cart, Order, OrderItem
from state.store import cargar_datos_ejemplo
from views import menu_principal

if __name__ == "__main__":
    cargar_datos_ejemplo()
    menu_principal()