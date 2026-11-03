

import timeit
import psycopg2
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Datos de la prueba
id_albergue = 6
noche = '2027-05-18'

# 1. CONEXIONES

PG = dict(
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", 5432)),
    user=os.getenv("POSTGRES_USER", "bda"),
    password=os.getenv("POSTGRES_PASSWORD", "cambiame"),
    dbname=os.getenv("POSTGRES_DB", "festival")
)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Abrimos PostgreSQL una sola vez
con = psycopg2.connect(**PG)
cur = con.cursor()


# 2. CONSULTA POSTGRESQL

def disponibilidad_postgres(id_albergue, noche):

    cur.execute("""
        SELECT a.plazas - COUNT(res.id_reserva)
        FROM albergues a
        LEFT JOIN reservas res
            ON a.id_albergue = res.id_albergue
            AND %s::date >= res.fecha_desde
            AND %s::date < res.fecha_desde + res.dias
        WHERE a.id_albergue = %s
        GROUP BY a.plazas
    """, (noche, noche, id_albergue))

    resultado = cur.fetchone()

    return resultado[0] if resultado else None


# 3. CONSULTA REDIS

def disponibilidad_redis(id_albergue, noche):

    clave = f"plazas:albergue:{id_albergue}:{noche}"

    libres = r.get(clave)

    return int(libres) if libres is not None else None


# 4. COMPROBAR CONEXIONES Y CALENTAR LAS CONSULTAS

print("PostgreSQL:", disponibilidad_postgres(id_albergue, noche))
print("Redis:", disponibilidad_redis(id_albergue, noche))


# 5. MEDIR TIEMPOS

medicion_pg = timeit.timeit(
    lambda: disponibilidad_postgres(id_albergue, noche),
    number=1000
)

medicion_redis = timeit.timeit(
    lambda: disponibilidad_redis(id_albergue, noche),
    number=1000
)


# 6. MOSTRAR RESULTADOS

print("\n--- TIEMPOS DE CONSULTA ---")

print(f"PostgreSQL: {medicion_pg / 1000 * 1000:.6f} ms de media")
print(f"Redis: {medicion_redis / 1000 * 1000:.6f} ms de media")


# 7. CERRAR CONEXIONES

cur.close()
con.close()
r.close()
