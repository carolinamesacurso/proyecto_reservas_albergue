import os
import psycopg2
import redis

from dotenv import load_dotenv

load_dotenv()

PG = dict(host=os.getenv("PGHOST", "localhost"), port=int(os.getenv("PGPORT", 5432)),
          user=os.getenv("POSTGRES_USER", "bda"), password=os.getenv("POSTGRES_PASSWORD", "cambiame"),
          dbname=os.getenv("POSTGRES_DB", "festival"))
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True)


 #Recoger albergue y peregrino de la base de datos y comprobar que existen
def consultar_albergue_plazas_totales(albergue_id):
    """Consulta las plazas totales de un albergue."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_albergue, plazas
            FROM albergues
            WHERE id_albergue = %s
        """, (albergue_id,))

        resultados = cur.fetchall()

        return resultados if resultados else None
    
def consultar_peregrino(peregrino_id):
    """Consulta la información de un peregrino específico."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_peregrino, nombre, email
            FROM peregrinos
            WHERE id_peregrino = %s
        """,(peregrino_id,))

        resultados = cur.fetchall()

        return resultados if resultados else None

#que estén en el rango de fechas de la reserva
#si miramos por fecha 2026-11-08 - albergeue_id = 1 
#recogemos la reserva que su fecha desde sea menor (2026-11-06) o iguaul y su fecha desde + dias sea mayor 
# (2026-11-06 + 3 = 2026-11-09 - (11-06 , 11-07, 11-08, 11-09)) - es decir, le tienes que sumar a la reserva 3 días 
# AND fecha_desde <= %s
# AND fecha_desde + dias > %s 

def consultar_reservas_peregrino(id_peregrino, noche):
    """Comprueba si un peregrino tiene una reserva para esa noche."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_reserva, id_peregrino, id_albergue,
                   fecha_desde, dias
            FROM reservas
            WHERE id_peregrino = %s
              AND fecha_desde <= %s
              AND fecha_desde + dias > %s
        """, (id_peregrino, noche, noche))

        resultados = cur.fetchall()

        return resultados if resultados else None

def consultar_reservas_noche(albergue, noche):
    """Cuenta las reservas que ocupan una noche en un albergue."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM reservas
            WHERE id_albergue = %s
              AND fecha_desde <= %s
              AND fecha_desde + dias > %s
        """, (albergue, noche, noche))

        resultado = cur.fetchone()

        return resultado[0]


# def reserva_atomica(key):
#     """Resta de forma atómica si hay plazas disponibles, si no hay plazas disponibles, vuelve a su estado original."""
#     libres = r.decr(key)
#     if libres >= 0:
#         return True
#     r.incr(key)  
#     return False
def reserva_atomica(key):
    """Descuenta una plaza de Redis si hay disponibilidad."""

    libres = r.decr(key)

    if libres >= 0:
        return True

    # No había plazas: recuperamos el contador
    r.incr(key)
    return False


def insertar_reserva(peregrino, albergue, noche):
    """Inserta una reserva en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            INSERT INTO reservas
                (id_peregrino, id_albergue, fecha_desde, dias)
            VALUES (%s, %s, %s, %s)
        """, (peregrino, albergue, noche, 1))




def reservar(albergue, noche, peregrino):
    """Registra una reserva en Redis y PostgreSQL."""

    # 1. Comprobar si existe el peregrino y el albergue
    peregrino_info = consultar_peregrino(peregrino)
    albergue_info = consultar_albergue_plazas_totales(albergue)

    if not peregrino_info or not albergue_info:
        print("El peregrino o el albergue no existen.")
        return False

    # 2. Comprobar si el peregrino ya tiene una reserva esa noche
    resultado = consultar_reservas_peregrino(peregrino, noche)

    if resultado:
        print("El peregrino ya tiene una reserva esa noche.")
        return False

    # 3. Crear la clave de Redis si no existe
    key = f"plazas:albergue:{albergue}:{noche}"

    if not r.exists(key):

        plazas_totales = albergue_info[0][1]

        plazas_ocupadas = consultar_reservas_noche(albergue, noche)

        plazas_libres = max(0, plazas_totales - plazas_ocupadas)

        r.set(key, plazas_libres, nx=True)

    # 4. Descontar una plaza en Redis
    if not reserva_atomica(key):
        print("No hay plazas disponibles.")
        return False

    # 5. Guardar la reserva en PostgreSQL
    try:
        insertar_reserva(peregrino, albergue, noche)

        print("Reserva realizada correctamente.")
        return True

    except psycopg2.Error as e:

        # 6. Si PostgreSQL falla, recuperar la plaza
        r.incr(key)

        print(f"Error al guardar la reserva: {e}")
        print("Se ha recuperado la plaza en Redis.")

        return False

    # 4. Guardar reserva en PostgreSQL
    # 5. Si PostgreSQL falla, devolver plaza a Redis
    # #revisar
    # if resultado:
    #     print("El peregrino ya tiene una reserva para esa noche:")
    #     for reserva in resultado:
    #         print(reserva)
    # else:
    #     print("El peregrino no tiene ninguna reserva esa noche.")
     
    #2. Comprobar si hay plazas libres para el albergue en la fecha indicada



    # r.hset(f"reserva:{albergue}:{noche}", peregrino, 1)

import sys
from datetime import date
if __name__ == "__main__":
    peregrino = int(sys.argv[1])
    albergue = int(sys.argv[2])
    noche = date.fromisoformat(sys.argv[3])

    reservar(albergue, noche, peregrino)