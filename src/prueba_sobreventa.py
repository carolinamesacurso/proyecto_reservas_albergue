from concurrent.futures import ThreadPoolExecutor

from src.reservas import reservar

albergue = 6

# Peregrinos que no tienen otra reserva esa noche
peregrinos = [2, 3, 4]

noche = "2026-11-09"

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