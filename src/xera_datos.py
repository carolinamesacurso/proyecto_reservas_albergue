
import argparse
import random
from datetime import date, timedelta


from faker import Faker

# ------------------------------------------------------------------ catálogos
# Concellos galegos de cada camiño, en orde de etapas. Podes engadir máis.
CAMIÑOS = {
    "Francés":   ["Pedrafita do Cebreiro", "Triacastela", "Samos", "Sarria", "Portomarín",
                  "Palas de Rei", "Melide", "Arzúa", "O Pino"],
    "Portugués": ["Tui", "O Porriño", "Redondela", "Pontevedra", "Caldas de Reis", "Padrón", "Teo"],
    "Norte":     ["Ribadeo", "Lourenzá", "Mondoñedo", "Abadín", "Vilalba", "Guitiriz", "Sobrado"],
    "Primitivo": ["A Fonsagrada", "Castroverde", "Lugo", "Friol", "Melide"],
    "Inglés":    ["Ferrol", "Neda", "Pontedeume", "Betanzos", "Abegondo", "Ordes"],
}
NOMES_ALBERGUE = ["Vieiras", "Pedra Miúda", "O Cruceiro", "A Ponte Vella", "Bordón", "A Cabaciña",
                  "Fonte Vella", "Os Carballos", "A Estrela", "Camiño Real", "Casa do Peregrino",
                  "A Xesta", "O Muíño", "Santa Mariña", "O Hórreo", "A Lareira", "Sete Fontes"]


def pendente(nome):
    print(f"  [pendente] {nome}() aínda non está feita")
    return []


# ------------------------------------------------------------------ xeración
def xera_albergues(n, rng):
 
    albergues = []
    for i in range(1, n + 1):
        camino = rng.choice(list(CAMIÑOS))
        concello = rng.choice(CAMIÑOS[camino])
        albergues.append({
            "id": i,
            "nome": f"Albergue {rng.choice(NOMES_ALBERGUE)} ({concello})",
            "camino": camino,
            "concello": concello,
            "prazas": rng.randint(8, 60),
            "prezo": float(rng.randint(10, 22)),
        })
    return albergues


def xera_peregrinos(n, rng, fake):
    """TODO ..."""

    # Relacionamos cada país con el idioma que usará Faker
paises = {
    "España": "es_ES",
    "Portugal": "pt_PT",
    "Alemania": "de_DE",
}

def xera_peregrinos(n, rng, fake):
    
    # Relacionamos cada país cun idioma de Faker para que os nomes teñan sentido
    paises = {
        "España": "es_ES",
        "Portugal": "pt_PT",
        "Alemania": "de_DE",
    }

    # Creamos un Faker para cada país
    fakers_pais = {
        pais: Faker(locale)
        for pais, locale in paises.items()
    }

    peregrinos = []

    for i in range(1, n + 1):
        # Elegimos un país al azar y usamos su Faker para generar el nombre
        pais = rng.choice(list(paises.keys()))
        fake_pais = fakers_pais[pais]

        nombre = fake_pais.first_name()
        apellidos = fake_pais.last_name()

        # se genera un número de documento sencillo y distinto para cada peregrino
        documento = f"DOC{i:06d}"
        # añadimos el número del peregrino para evitar correos repetidos
        email = f"peregrino{i}@example.com"
        # fecha de nacimiento para cada peregrino
        fecha_nacimiento = fake_pais.date_of_birth()

        peregrino = {
            "id": i,
            "nome": nombre,
            "apelidos": apellidos,
            "documento": documento,
            "email": email,
            "data_nacemento": fecha_nacimiento,
            "pais": pais,
        }

        peregrinos.append(peregrino)

    return peregrinos
    

def xera_reservas(n, albergues, peregrinos, desde, dias, rng):
    
    reservas = []

    # guardamos la ocupación de cada albergue por fecha
    ocupacion = {}

    # guardamos las noches que ya tiene reservadas cada peregrino
    noches_peregrinos = {}

    # Intentamos generar las reservas una a una hasta llegar a la cantidad pedida
    for i in range(1, n + 1):
        # elegimos uno de los días disponibles dentro del periodo
        dias_desde_inicio = rng.randint(0, dias - 1)
        fecha = desde + timedelta(days=dias_desde_inicio)
        # elegimos al azar quién hace la reserva y en qué albergue
        peregrino = rng.choice(peregrinos)
        albergue = rng.choice(albergues)
        # miramos qué noches tiene ya reservadas este peregrino
        noches_reservadas = noches_peregrinos.get(peregrino["id"], set())

        # si ya tiene una reserva ese día, probamos con otra combinación
        if fecha in noches_reservadas:
            continue

        # usamos el albergue y la fecha para saber cuántas plazas hay ocupadas esa noche
        clave_ocupacion = (albergue["id"], fecha)
        plazas_ocupadas = ocupacion.get(clave_ocupacion, 0)

        # si ya están ocupadas todas las plazas, buscamos otra reserva
        if plazas_ocupadas >= albergue["prazas"]:
            continue

        # hasta aqui la reserva cumple las dos reglas
        reserva = {
            "id": len(reservas) + 1,
            "peregrino_id": peregrino["id"],
            "albergue_id": albergue["id"],
            "fecha": fecha,
        }

        # se añade la nueva reserva a la lista
        reservas.append(reserva)

         # actualizamos la ocupación del albergue para esa noche
        ocupacion[clave_ocupacion] = plazas_ocupadas + 1

        # guardamos también la noche reservada por este peregrino
        noches_reservadas.add(fecha)
        noches_peregrinos[peregrino["id"]] = noches_reservadas
    return reservas


def xera_fichas(albergues, rng, fake):
    
    # aqui iremos guardando una ficha diferente para cada albergue
    fichas = []

        # Recorremos los albergues que ya hemos generado anteriormente
    for albergue in albergues:
        ficha = {
            "albergue_id": albergue["id"],
            "nombre": albergue["nome"],
            
        }

        # elegimos algunos servicios para que no todos los albergues sean iguales
        servicios_disponibles = [
            "cocina",
            "lavadora",
            "wifi",
            "almuerzo",
        ]

        cantidad_servicios = rng.randint(1, len(servicios_disponibles))
        ficha["servicios"] = rng.sample(
            servicios_disponibles, cantidad_servicios
        )

        # generamos un horario sencillo de apertura y cierre
        hora_apertura = rng.randint(11, 15)
        hora_cierre = rng.randint(21, 23)

        ficha["horario"] = {
            "apertura": f"{hora_apertura:02d}:00",
            "cierre": f"{hora_cierre:02d}:00",
        }

        # algunos albergues tienen datos de contacto y otros no
        if rng.random() < 0.6:
            ficha["contacto"] = {
                "telefono": fake.phone_number(),
                "web": fake.url(),
            }

        # no todos los albergues tienen información sobre si admiten perros
        if rng.random() < 0.5:
            ficha["admite_perros"] = rng.choice([True, False])

        # algunos tienen un espacio específico para guardar bicicletas
        if rng.random() < 0.6:
            ficha["bicicletas"] = {
                "garaje": rng.choice([True, False]),
                "plazas": rng.randint(4, 20),
            }

        # cada albergue puede atender en uno o varios idiomas
        idiomas_disponibles = ["gallego", "castellano", "inglés"]
        cantidad_idiomas = rng.randint(1, len(idiomas_disponibles))
        ficha["idiomas"] = rng.sample(idiomas_disponibles, cantidad_idiomas)
        # se añaden opiniones solo a algunos albergues
        if rng.random() < 0.5:
            opiniones = []

            cantidad_opiniones = rng.randint(1, 3)

            for _ in range(cantidad_opiniones):
                opinion = {
                    "autor": fake.first_name(),
                    "nota": rng.randint(1, 5),
                    "texto": fake.sentence(),
                }
                opiniones.append(opinion)

            ficha["opiniones"] = opiniones
        # indicamos también quién es el titular
        if rng.random() < 0.4:
            ficha["titularidad"] = rng.choice([
                "Xunta de Galicia",
                "Municipal",
                "Privada",
            ])
        # Algunos albergues tienen datos de contacto y otros no
        if rng.random() < 0.6:
            ficha["contacto"] = {
                "telefono": fake.phone_number(),
                "web": fake.url(),
            }
            
        fichas.append(ficha)

    return fichas


# ------------------------------------------------------------------ carga
def carga_postgres(albergues, peregrinos, reservas):
    """TODO: crea as táboas (ou usa un script SQL de inicio) e insire os datos."""
    pendente("carga_postgres")


def carga_mongo(fichas):
    """TODO: garda as fichas nunha colección de MongoDB."""
    pendente("carga_mongo")


# ------------------------------------------------------------------ main
def mostra(titulo, filas, cantas=2):
    print(f"\n{titulo}: {len(filas)}")
    for f in filas[:cantas]:
        print(f"  {f}")


def main():
    ap = argparse.ArgumentParser(description="Xera e carga datos de proba de Camiño Aberto")
    ap.add_argument("--albergues", type=int, default=40)
    ap.add_argument("--peregrinos", type=int, default=1500)
    ap.add_argument("--reservas", type=int, default=5000)
    ap.add_argument("--semente", type=int, default=42, help="mesma semente → mesmos datos")
    ap.add_argument("--desde", type=date.fromisoformat, default=date(2027, 5, 1),
                    help="primeira noite da tempada (AAAA-MM-DD)")
    ap.add_argument("--dias", type=int, default=30, help="número de noites da tempada")
    ap.add_argument("--sen-carga", action="store_true", help="xera e mostra, pero non carga nada")
    args = ap.parse_args()

    rng = random.Random(args.semente)
    fake = Faker("es_ES")
    # TODO: Faker tamén ten a súa propia semente. Sen ela, os nomes cambian en cada execución.

    print(f"Semente {args.semente} · tempada {args.desde} + {args.dias} noites")
    albergues = xera_albergues(args.albergues, rng)
    peregrinos = xera_peregrinos(args.peregrinos, rng, fake)
    reservas = xera_reservas(args.reservas, albergues, peregrinos, args.desde, args.dias, rng)
    fichas = xera_fichas(albergues, rng, fake)

    mostra("Albergues", albergues)
    mostra("Peregrinos", peregrinos)
    mostra("Reservas", reservas)
    mostra("Fichas", fichas, 1)

    if not args.sen_carga:
        carga_postgres(albergues, peregrinos, reservas)
        carga_mongo(fichas)


if __name__ == "__main__":
    main()
