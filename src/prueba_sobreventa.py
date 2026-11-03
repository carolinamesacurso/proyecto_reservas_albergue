from concurrent.futures import ThreadPoolExecutor

from src.reservas import reservar
#Albergue 9 | Noche: 2027-05-20 | Plazas libres: 1

albergue = 9

# Peregrinos que no tienen otra reserva esa noche
peregrinos = [2,4]

noche = "2027-05-20"

with ThreadPoolExecutor(max_workers=len(peregrinos)) as executor:

    resultados = list(
        executor.map(
            lambda peregrino: reservar(
                albergue,
                noche,
                peregrino
            ),
            peregrinos
        )
    )

exitosas = sum(resultados)
rechazadas = len(resultados) - exitosas

print("\n--- RESULTADO DE LA PRUEBA ---")
print(f"Albergue: {albergue}")
print(f"Noche: {noche}")
print("Plazas iniciales: 1")
print(f"Solicitudes: {len(peregrinos)}")
print(f"Aceptadas: {exitosas}")
print(f"Rechazadas: {rechazadas}")