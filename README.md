# P1 · Reservas de albergues

En este proyecto realizaremos la gestión de las reservas de albergues con diferentes tipos de tecnologías.

Crearemos una red de datos donde manejaremos el guardado de datos en postgres, las plazas disponibles en redis y las fichas de cada albergue en mongodb.

## Aquitectura del sistema
### 2.1 PostgreSQL
- Utilizaremos este motor de bases de datos para guardar y gestionar datos relacionales, es decir, reserva, albergues y peregrinos.
- Esto debido a que podremos crear tablas que se puedan conectar entre ellas atraves de un modelo ER ya que nuestra tabla de reservas necesita de 1 peregrino y 1 albergue para crear una fila de datos.
- Además de que la estructura de nuestras tablas no va a ser modificada de una manera concurrente , es decir , seguramente durante nuestro desarrollo no cambiaremos datos o relaciones y seguirán una misma estructura.
### 2.2 Redis
- Para poder manejar nuestras plazas libres necesitaremso un motos el cual nos garantize que no tendremos una sobreventa de ellas si hay reservas simultaneas.
- Para ello es fundamental utilizar operaciones atómicas las cuales permitan rechazar la reserva y decrementar o incrementar contadores de una manera rapida y sencilla.
- También se utilizará para realizar consultas habituales y cargarlas en caché para que se puedan eliminar de memoria despues de un tiempo , todo esto para no ocupar demasiada memoria con consultas repetitivas.
### 2.3 MongoDB
- Com nuestras fichas de albergues se distingirán de los demás datos mencionados ya que no seguirñan un patrón de datos utilizaremos mongodb.
- Esto debido a que nso permite gestionar colecciones con diferentes estructuras y no crear parametros nulos inecesarios.
### 2.4 Comunicación entre los sistemas
- Redis-postgresql : En esta pareja se comunican mediante la creación de reservas , ya que si no existen plazas suficientes no se crearán reservas.
    - En este caso redis guardará en su estructura la disponibilidad libre de cada día según las reservas de postgreSQL al iniciar redis
    - Cuando se quiera realizar una reserva después de realizar las comprobaciones de existencias en postgres se decrementará el contador en redis, como último paso se creará la reserva en redis 

## 3. Instalación y puesta en marcha

### 1. Clonar el proyecto (ubuntu)

Crea una estructura de carpetas para poder clonar el repositorio dentro con los siguientes comandos:

```powershell
mkdir carpetaEjemplo
cd carpetaEjemplo
```

### 2. Crea el environment y actívalo
```powershell
python3 \-m venv .venv
source .venv/bin/activate
```
### 3. Clona el repositorio

```powershell
git clone https://github.com/carolinamesacurso/proyecto_reservas_albergue
```

### 4. Configura variables e instalar librerías
#### 4.1 Pasos para arrancar el proyecto
Para este proceso deberás de abrir el proyecto con visual studio con el siguiente comando

```powershell
code .
```

El proyecto te proporcionará un '.env.example' el cual tendrás que copiar para crear el fichero '.env' donde realizaremos los siguientes pasos.

Modifica estas variables en '.env' para configurar el usuario , contraseña y base de datos a utilizar

```
POSTGRES_USER=***
POSTGRES_PASSWORD=***
POSTGRES_DB=***
MONGO_USER=***
MONGO_PASSWORD=***
MONGO_DB=***
PGHOST=***
REDIS_HOST=***
MONGO_HOST=***

```

Para instalar las dependencias necesarias ejecuta este comando dentro del enviroment

```powershell
pip install -r requirements.txt
```

A la hora de levantar los servicios ejecutaremos el siguiente comando con la app docker desktop inicializada y configurada.
```powershell
docker compose up
```

#### 4.2 Generar datos (xera_datos.py)


#### 4.3 Ejecución de diferentes partes de la aplicación

- Iniciar contenedores de plazas libres
    - Para ello después de generar los datos procedos a situarnos en la carpeta src desde la raíz del proyecto y ejecutar el comando llamando al siguiente archivo 
     ```powershell
    cd src
    python iniciar_redis.py
    ```

- Realizar reservas con postgresql y redis:
    - Para poder realizar reservas y decrementar/incrementar los contadores en redis procederemos a seguir la estructura del siguiente comando (peregrino, albergue, noche) :

      ```powershell
        cd src
        python reservas.py 1 5 2026-11-09
        ```
    


## 4. Decisiones de diseño
### 4.1 Estructura de claves Redis
- Para la estructura de claves en redis seguimos este razonamiento:
    - Al necesitar una estructura donde mostrar las plazas libres de cada albergue por noche , crearemos una clave donde esta se una combinación del albergue por cada una de las noches.
    - En el siguiente ejemplo mostramos un ejemplo de ello , mostrando el albergue 1 cuantas plazas libres tiene el día 2026-11-05

    ```
    GET plazas:albergue:3:2026-11-05
    ```
### 4.2 TTL
### 4.3 Estructura de fichas MongoDB
### 4.4 Gestión de reservas y concurrencia
- Para realizar la gestión de las reservas mostraremos los siguientes mensajes para controlar casos erroneos o mostrar que se han creado correctamente :
    - 'El peregrino ya tiene una reserva esa noche.' si encontramos que el peregrino tiene una reserva que coincide con la fecha a tratar
    - 'El peregrino o el albergue no existen.' Si intentamos crear una reserva con datos inexistentes 
    - 'Reserva realizada correctamente' cuando se ha creado la reserva sin ningún error.
    - 'No hay plazas disponibles.' Cuando accedemos a una fecha de un albergue que no tiene plazas libres

- En el caso de la concurrencia controlamos esa parte a partir de redis con los métodos dcr() e incr() , esto para realizar la operación de forma atómica y,debido a que si ocurre algún error o sobreventa cancelar y volver a incremental
    - decr() en los casos de que se ha realizado correctamente la reserva y tiene plazas disponibles
    - incr() en el caso de que al decr() al principio pasen los siguientes casos: nos encontramos que al comprobar si hay plazas disponibles después de decr() que no cumple con esto o si falla al insertar en postgres . Ya que aunqeu se haya conseguido decremental no se ha realizado una correcta reserva y los datos de redis y postgres no pueden estar en conflicto.

## 5. Prueba de sobreventa
- Para hacer la prueba de sobreventa nos situaremos en la carpeta raíz del proyecto y ejecutaremos este comando con nuestro docker compose reiniciado:
```
docker compose down -v
docker compose up
python -m src.prueba_sobreventa
```

- En esta prueba se realizará la sobreventa sobre nuestro albergue de prueba con dos plazas libres 
    - Lanzamos varios hilos simultaneos donde variso peregrinos intentarán reservar del mismo día para el mismo albergue , encontrándose que solo hay una plaza disponible.

```
No hay plazas disponibles.
No hay plazas disponibles.
Reserva realizada correctamente.

--- RESULTADO DE LA PRUEBA ---
Albergue: 6
Noche: 2026-11-09
Plazas iniciales: 1
Solicitudes: 3
Aceptadas: 1
Rechazadas: 2
```

## 7. Mediciones de rendimiento
### 7.1 PostgreSQL frente a Redis
- Para hacer la prueba de medición de tiempo nos situaremos en la carpeta raíz src y ejecutaremos este comando con nuestro docker compose reiniciado:
```
docker compose down -v
docker compose up

python medir_postgres_redis.py
PostgreSQL: 24
Redis: 24

--- TIEMPOS DE CONSULTA ---
PostgreSQL: 0.280031 ms de media
Redis: 0.187290 ms de media
```
- Conclusiones de esta prueba:
    - Para construir las consultas en nuestro archivo nos encontramos que postgres necesita ejecutar una consulta. SQL relacionando tablas y realizando el calculo 
    - Mientras que en redis recuperamos directamente el contador de disponibilidad sin ninguna operación de por medio.
    - Comparando los tiempos de consulta descubrimos que aunque ambos sistemas devuelven el mismo resultado redis fue considerablemente más rápudo debido al modo de recuperación de ambas consultas, es decir , para consultas que no necesitan mucha complejidad o sean rápidas y recurrentes necesitaremos redis.


## 8. Uso de inteligencia artificial

1. Revisar una explicación más detallada del código a utilizar , como en el caso de los hilos en la medición de tiempos o la prueba de simultaniedad.

2. Contrastar errores que se han producido a la hora de crear código manualmente.

3. Generar código de ejemplo para poder aplicarlo a la hora de recoger datos por consola en reservas o razonar orden de ejecución.
