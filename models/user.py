from __future__ import annotations

import hashlib
import uuid
from typing import List

from .address import Address

class User:
    _users_by_email: dict = {}

    def __init__(self, name, email, password, phone):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email.lower().strip()
        self.password = password
        self.phone = phone
        self.addresses: List[Address] = []

    @staticmethod
    def _hash(p):
        return hashlib.sha256(p.encode()).hexdigest()

    @classmethod
    def registrarse(cls, name, email, password, phone):
        email = email.lower().strip()
        if email in cls._users_by_email:
            raise ValueError("Ese email ya está registrado")
        u = cls(name, email, cls._hash(password), phone)
        cls._users_by_email[email] = u
        return u

    @classmethod
    def ingresar(cls, email, password):
        email = email.lower().strip()
        u = cls._users_by_email.get(email)
        if not u or u.password != cls._hash(password):
            raise ValueError("Email o contraseña incorrectos")
        return u

    def actualizar_datos(self, name=None, email=None, phone=None, password=None):
        if email:
            ne = email.lower().strip()
            if ne != self.email:
                if ne in self._users_by_email:
                    raise ValueError("Email ya en uso")
                self._users_by_email.pop(self.email, None)
                self.email = ne
                self._users_by_email[ne] = self
        if name:
            self.name = name
        if phone:
            self.phone = phone
        if password:
            self.password = self._hash(password)