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

def inicializar_redis():
    pass

def consultar_albergues_plazas_totales():
    """Consulta todos los ids de albergues con sus plazas totales almacenados en PostgreSQL."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_albergue,plazas
            FROM albergues
        """)

        resultados = cur.fetchall()

        for albergue in resultados:
            print(albergue)


print("\nALBERGUES REGISTRADOS:")
consultar_albergues_plazas_totales()


def consultar_reservas():
    """Consulta todos las reservas actuales."""

    with psycopg2.connect(**PG) as con, con.cursor() as cur:
        cur.execute("""
            SELECT id_reserva, id_peregrino, id_albergue, fecha_desde, dias
            FROM reservas
        """)

        resultados = cur.fetchall()

        for reserva in resultados:
            print(reserva)


print("\nRESERVAS ACTUALES:")
consultar_reservas()


from datetime import timedelta


def calcular_plazas_libres():
    """
    Calcula las plazas libres de cada albergue para cada noche,
    teniendo en cuenta las reservas almacenadas en PostgreSQL.

    """

    # 1. Consultar albergues y sus capacidades
    with psycopg2.connect(**PG) as con, con.cursor() as cur:

        cur.execute("""
            SELECT id_albergue, plazas
            FROM albergues
        """)

        albergues = cur.fetchall()

        # 2. Consultar las reservas existentes
        cur.execute("""
            SELECT id_albergue, fecha_desde, dias
            FROM reservas
        """)

        reservas = cur.fetchall()

    # 3. Inicializar la ocupación a cero
    ocupacion = {}

   # 4. Recorrer las reservas y contar las noches ocupadas
    for id_albergue, fecha_desde, dias in reservas:

        for i in range(dias):  # si son 2 -> 0,1

            noche = fecha_desde + timedelta(days=i)

            clave = (id_albergue, noche)

            if clave not in ocupacion:
                ocupacion[clave] = 0

            ocupacion[clave] += 1


    # 7. Calcular las plazas libres
    capacidades = dict(albergues) # {1: 10, 2:5} albergue 1 tiene 10 plazas, albergue 2 tiene 5 plazas
    #pillamos la capacidaa total del idalbergeu de esa vuelta y la restamos a las plazas ocupadas de ocupación
    #recorremos esa lista de ocupación ya que tiene todas las fechas y vamos configurando con sus albergues y sus fechas las plazas libres que nos quedan
    plazas_libres = {}
    # significa que clave es (id_albergue, noche) y ocupadas es el numero de reservas para esa noche que hemos sumado antes
    # (12, 03/11):1 clave:ocupadas
    for clave, ocupadas in ocupacion.items(): 

        id_albergue, noche = clave #clave es  clave = (id_albergue, noche) /dividimos clave en id_albergue y noche para poder acceder a capacidades[id_albergue] y calcular las plazas libres

        libres = capacidades[id_albergue] - ocupadas 
        #recogemos el valor de id_albergue de esta vuelta(12) de capacidades (albergues) ya que es su capacidad total de plazas 
        # asi que le restamos las ocupadas de la lista de ocupaciones actuales
        if libres < 0:
            raise ValueError(
                f"Sobreocupación en albergue {id_albergue}, noche {noche}"
            )
        plazas_libres[clave] = libres #y guardamos en plazas_libres la clave (id_albergue, noche) y el valor de libres que acabamos de calcular

    return plazas_libres


resultado = calcular_plazas_libres()

for (id_albergue, noche), libres in resultado.items():
    print(
        f"Albergue {id_albergue} | "
        f"Noche: {noche} | "
        f"Plazas libres: {libres}"
    )


#set las plazas
def inicializar_redis():
    """Inicializa los contadores de plazas libres en Redis."""

    plazas_libres = calcular_plazas_libres()

    for (id_albergue, noche), libres in plazas_libres.items():

        clave = f"plazas:albergue:{id_albergue}:{noche}"

        r.set(clave, libres)

    print("Contadores de Redis inicializados correctamente.")

inicializar_redis()