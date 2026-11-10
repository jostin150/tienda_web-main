import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "tienda")

IVA_DEFAULT = 0.19
ENVIO_BASE = 10_000.0
ENVIO_GRATIS_DESDE = 150_000.0

# Correos que tienen rol de administrador (separados por coma en el .env)
ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("ADMIN_EMAILS", "admin@tienda.com").split(",")
    if e.strip()
}
