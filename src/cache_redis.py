
import os
import json
from datetime import date

import psycopg2
import redis
from dotenv import load_dotenv

load_dotenv()

# Tiempo que guardaremos los resultados en Redis: 60 segundos
TTL = 60

# Conexión a Redis
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Configuración de PostgreSQL
PG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "bda"),
    "password": os.getenv("POSTGRES_PASSWORD", "cambiame"),
    "dbname": os.getenv("POSTGRES_DB", "festival")
}


def buscar_albergues(camino, noche):
    # Clave propia para la caché, distinta de los contadores de reservas
    clave = f"cache:albergues:{camino}:{noche}"

    # 1. Intentamos recuperar el resultado desde Redis
    datos_cache = r.get(clave)

    if datos_cache is not None:
        print("Resultado obtenido de Redis (HIT)")
        return json.loads(datos_cache)

    # 2. Si no existe, consultamos PostgreSQL
    print("Resultado obtenido de PostgreSQL (MISS)")

    conexion = psycopg2.connect(**PG)

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id_albergue,
                    a.nombre,
                    a.camino,
                    a.plazas - COUNT(res.id_reserva) AS plazas_libres
                FROM albergues a
                LEFT JOIN reservas res
                    ON a.id_albergue = res.id_albergue
                    AND %s::date >= res.fecha_desde
                    AND %s::date < res.fecha_desde + res.dias
                WHERE a.camino = %s
                GROUP BY a.id_albergue, a.nombre, a.camino, a.plazas
                HAVING a.plazas > COUNT(res.id_reserva)
                ORDER BY a.nombre
            """, (noche, noche, camino))

            filas = cursor.fetchall()

        resultados = [
            {
                "id_albergue": fila[0],
                "nombre": fila[1],
                "camino": fila[2],
                "plazas_libres": int(fila[3])
            }
            for fila in filas
        ]
    finally:
        conexion.close()

    # 3. Guardamos el resultado en Redis durante 60 segundos
    r.setex(clave, TTL, json.dumps(resultados))

    return resultados


def invalidar_cache_albergue(albergue_id, noche):
    """Elimina la caché del Camino de un albergue para una noche."""

    conexion = psycopg2.connect(**PG)

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT camino FROM albergues WHERE id_albergue = %s",
                (albergue_id,)
            )
            resultado = cursor.fetchone()
    finally:
        conexion.close()

    if resultado is None:
        return False

    camino = resultado[0]
    clave = f"cache:albergues:{camino}:{noche}"

    eliminadas = r.delete(clave)

    print(f"Claves de caché eliminadas: {eliminadas}")
    return True


if __name__ == "__main__":
    camino = "Francés"
    noche = "2027-05-15"

    print("\n--- PRIMERA CONSULTA ---")
    resultado = buscar_albergues(camino, noche)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    print("\n--- SEGUNDA CONSULTA ---")
    resultado = buscar_albergues(camino, noche)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    clave = f"cache:albergues:{camino}:{noche}"
    print("\nTTL restante:", r.ttl(clave), "segundos")
