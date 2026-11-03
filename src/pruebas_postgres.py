import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

PG = dict(host=os.getenv("PGHOST", "localhost"), port=int(os.getenv("PGPORT", 5432)),
          user=os.getenv("POSTGRES_USER", "bda"), password=os.getenv("POSTGRES_PASSWORD", "cambiame"),
          dbname=os.getenv("POSTGRES_DB", "festival"))

def insertar_albergue(nome, concello, camino, prazas, prezo):
    """Inserta un albergue en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            INSERT INTO albergues (nombre, concello, camino, plazas, precio)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_albergue
        """, (nome, concello, camino, prazas, prezo))

        return cur.fetchone()[0]


def insertar_peregrino(nome, apellido, pais, email, documento, nacimiento):
    """Inserta un peregrino en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            INSERT INTO peregrinos
            (nombre, apellido, pais, email, documento_identidad, fecha_nacimiento)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_peregrino
        """, (nome, apellido, pais, email, documento, nacimiento))

        return cur.fetchone()[0]


def insertar_reserva(id_albergue, id_peregrino, fecha_desde, dias):
    """Inserta una reserva en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            INSERT INTO reservas (id_albergue, id_peregrino, fecha_desde, dias)
            VALUES (%s, %s, %s, %s)
            RETURNING id_reserva
        """, (id_albergue, id_peregrino, fecha_desde, dias))

        return cur.fetchone()[0]


# ==========================================
# DATOS DE PRUEBA
# ==========================================

# ALBERGUES
albergues = [
    ("Camino Real", "Sarria", "Camino Frances", 25, 15.00),
    ("Albergue Peregrino", "Portomarin", "Camino Frances", 30, 18.00),
    ("Santa Maria", "Palas de Rei", "Camino Frances", 20, 12.50),
    ("Albergue Santiago", "Melide", "Camino Frances", 35, 16.00),
    ("Ultreia", "Tui", "Camino Portugues", 28, 14.00)
]

ids_albergues = []

for albergue in albergues:
    ids_albergues.append(insertar_albergue(*albergue))


# PEREGRINOS
peregrinos = [
    ("Ana", "Garcia", "España", "ana@gmail.com", "12345678A", "1995-04-12"),
    ("Carlos", "Rodriguez", "Portugal", "carlos@gmail.com", "12345678B", "1988-09-23"),
    ("Laura", "Fernandez", "Francia", "laura@gmail.com", "12345678C", "2000-01-15"),
    ("Pedro", "Lopez", "Alemania", "pedro@gmail.com", "12345678D", "1992-06-30"),
    ("Maria", "Martinez", "Italia", "maria@gmail.com", "12345678E", "1998-11-08")
]

ids_peregrinos = []

for peregrino in peregrinos:
    ids_peregrinos.append(insertar_peregrino(*peregrino))


# RESERVAS
reservas = [
    (ids_albergues[0], ids_peregrinos[0], "2026-11-05", 2),
    (ids_albergues[1], ids_peregrinos[1], "2026-11-05", 1),
    (ids_albergues[2], ids_peregrinos[2], "2026-11-06", 2),
    (ids_albergues[3], ids_peregrinos[3], "2026-11-07", 1),
    (ids_albergues[4], ids_peregrinos[4], "2026-11-08", 3)
]

for reserva in reservas:
    insertar_reserva(*reserva)

print("Datos de prueba insertados correctamente.")


def consultar_albergues():
    """Consulta todos los albergues almacenados en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_albergue, nombre, concello, camino, plazas, precio
            FROM albergues
        """)

        resultados = cur.fetchall()

        for albergue in resultados:
            print(albergue)


print("\nALBERGUES REGISTRADOS:")
consultar_albergues()