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

Para generar los datos de prueba partimos del archivo `xera_datos.py` que nos proporcionó el profesor. Este archivo tenía algunas partes sin completar, por lo que tuvimos que terminarlo para poder generar los datos que necesitábamos.

Con este script generamos los siguientes datos:

- 40 albergues en PostgreSQL.
- 1500 peregrinos en PostgreSQL.
- 5000 reservas en PostgreSQL.
- 40 fichas de albergues en MongoDB.

Para ejecutarlo nos situamos en la carpeta raíz del proyecto, con los contenedores de Docker funcionando, y utilizamos el siguiente comando:

```bash
python -m src.xera_datos
```

Una vez ejecutado, comprobamos que los datos se habían guardado correctamente en las dos bases de datos.

Estos datos los utilizaremos para realizar las pruebas de reservas, las consultas y las copias de seguridad.

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
      python reservas.py 1 18 2027-05-01
    ```

## 4. Decisiones de diseño

### 4.1 Estructura de claves Redis

- Para la estructura de claves en redis seguimos este razonamiento:

  - Al necesitar una estructura donde mostrar las plazas libres de cada albergue por noche , crearemos una clave donde esta se una combinación del albergue por cada una de las noches.
  - En el siguiente ejemplo mostramos un ejemplo de ello , mostrando el albergue 1 cuantas plazas libres tiene el día 2027-05-01

  ```
  GET plazas:albergue:18:2027-05-01
  ```

### 4.2 TTL

Para las consultas de información de los albergues hemos utilizado Redis como caché, de manera que no sea necesario consultar PostgreSQL cada vez que se pide la misma información.

Para ello completamos el archivo `src/cache_redis.py`, donde primero comprobamos si los datos están guardados en Redis. Si están disponibles, los recuperamos directamente y, si no están, realizamos la consulta a PostgreSQL y guardamos el resultado en Redis.

Hemos establecido un TTL de 60 segundos, por lo que los datos guardados en caché se eliminan automáticamente cuando pasa ese tiempo.

Para comprobar que funcionaba realizamos varias pruebas:

- **MISS:** la primera consulta no encuentra los datos en Redis y los recupera de PostgreSQL.
- **HIT:** al repetir la consulta antes de los 60 segundos, los datos se recuperan directamente de Redis.
- **Caducidad:** esperamos a que pasaran los 60 segundos y comprobamos que la clave había desaparecido.
- **Invalidación:** probamos la función `invalidar_cache_albergue()` para eliminar los datos guardados de un albergue cuando sea necesario actualizarlos.

Para comprobar el tiempo de vida de una clave utilizamos el comando:

```bash
redis-cli TTL nombre_de_la_clave
```

Cuando la clave ya había caducado, Redis devolvió `-2`, indicando que ya no existía.

La función de invalidación está implementada y probada, aunque todavía queda conectarla con el proceso de creación de reservas para que se ejecute automáticamente cuando cambien los datos.

### 4.3 Estructura de fichas MongoDB

Para guardar las fichas de los albergues utilizamos MongoDB, ya que nos permite almacenar documentos que no tienen por qué tener todos la misma estructura.

En nuestro caso, no todos los albergues tienen la misma información, por lo que algunos documentos pueden tener campos que otros no necesitan.

Esto nos permite guardar la información de cada albergue sin tener que añadir campos vacíos cuando no disponemos de algún dato.

Las fichas se generan mediante el archivo `xera_datos.py`, que completamos a partir del código inicial proporcionado por el profesor.

Durante las pruebas generamos 40 fichas de albergues en MongoDB y comprobamos que se habían guardado correctamente.

De esta forma utilizamos PostgreSQL para los datos relacionados con las reservas y MongoDB para la información más flexible de los albergues.
Para comprobar cómo se guardan las fichas, consultamos la colección `fichas` de MongoDB y recuperamos un documento con `findOne()`.

Este es uno de los albergues que hemos generado:

```javascript
{
  albergue_id: 1,
  nombre: 'Albergue A Estrela (Pedrafita do Cebreiro)',
  servicios: [
    'almuerzo'
  ],
  horario: {
    apertura: '11:00',
    cierre: '23:00'
  },
  contacto: {
    telefono: '+34 921 10 80 87',
    web: 'https://servicios.com/'
  },
  bicicletas: {
    garaje: false,
    plazas: 11
  },
  idiomas: [
    'gallego',
    'castellano',
    'inglés'
  ],
  opiniones: [
    {
      autor: 'Chuy',
      nota: 2,
      texto: 'Tempore nulla odit a veritatis vitae vel.'
    },
    {
      autor: 'Alma',
      nota: 3,
      texto: 'Et corporis officia soluta occaecati.'
    }
  ],
  titularidad: 'Xunta de Galicia'
}
```

En este ejemplo podemos ver que algunos campos contienen listas, como `servicios` e `idiomas`, mientras que otros contienen información agrupada, como `horario`, `contacto` o `bicicletas`.

También podemos guardar varias opiniones dentro de una misma ficha. Esto nos permite tener toda la información del albergue en un único documento.

La principal ventaja es que podemos añadir o quitar campos según la información disponible de cada albergue, sin tener que modificar la estructura de todas las fichas.

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
    Reserva realizada correctamente.

    --- RESULTADO DE LA PRUEBA ---
    Albergue: 9
    Noche: 2027-05-20
    Plazas iniciales: 1
    Solicitudes: 2
    Aceptadas: 1
    Rechazadas: 1
```

## 6. Copias de seguridad

Para realizar las copias de seguridad de las bases de datos hemos creado el script `src/copia.sh`, que permite guardar una copia de PostgreSQL y otra de MongoDB.

Para ello utilizamos `pg_dump` en PostgreSQL y `mongodump` en MongoDB. Las copias se guardan dentro de la carpeta `copias/`, creando una subcarpeta con la fecha y hora de cada ejecución para no sobrescribir las anteriores.

Para ejecutar el script desde la raíz del proyecto utilizamos:

```bash
bash src/copia.sh
```

En nuestras pruebas se creó la siguiente carpeta:

```text
copias/2026-11-03_19-36-32/
├── postgres.dump
└── mongo.archive.gz
```

Los archivos generados tenían un tamaño aproximado de 75 KB para PostgreSQL y 4,6 KB para MongoDB.

### 6.1 Comprobación de las copias

Para comprobar que las copias funcionaban, realizamos una restauración de ambas bases de datos sin modificar las originales.

En PostgreSQL restauramos la copia en una base de datos llamada `prueba_restauracion` y comprobamos que contenía:

```text
Albergues: 40
Peregrinos: 1500
Reservas: 5000
```

También restauramos la copia de MongoDB en otra base de datos llamada `prueba_restauracion`, donde comprobamos que se habían recuperado las 40 fichas de albergues.

Con estas pruebas comprobamos que podíamos recuperar los datos guardados en las copias de seguridad.

La carpeta `copias/` está incluida en `.gitignore` para evitar subir estos archivos al repositorio de GitHub.

## 7. Mediciones de rendimiento

### 7.1 PostgreSQL frente a Redis

- Para hacer la prueba de medición de tiempo nos situaremos en la carpeta raíz src y ejecutaremos este comando con nuestro docker compose reiniciado:

```
docker compose down -v
docker compose up

python medir_postgres_redis.py
PostgreSQL: 15
Redis: 15

--- TIEMPOS DE CONSULTA ---
PostgreSQL: 0.548431 ms de media
Redis: 0.191276 ms de media

```

- Conclusiones de esta prueba:
  - Para construir las consultas en nuestro archivo nos encontramos que postgres necesita ejecutar una consulta. SQL relacionando tablas y realizando el calculo
  - Mientras que en redis recuperamos directamente el contador de disponibilidad sin ninguna operación de por medio.
  - Comparando los tiempos de consulta descubrimos que aunque ambos sistemas devuelven el mismo resultado redis fue considerablemente más rápudo debido al modo de recuperación de ambas consultas, es decir , para consultas que no necesitan mucha complejidad o sean rápidas y recurrentes necesitaremos redis.

### 7.2 Consumo de recursos Docker

También hemos comprobado los recursos que consumen los tres contenedores del proyecto: PostgreSQL, Redis y MongoDB.

Para realizar la prueba, con los contenedores funcionando, ejecutamos desde la terminal:

```bash
docker stats --no-stream
```

Este comando nos permite consultar el consumo de CPU y memoria de cada contenedor en ese momento.

Los resultados que obtuvimos fueron los siguientes:

| Contenedor |    CPU |   Memoria | Porcentaje de memoria |
| ---------- | -----: | --------: | --------------------: |
| PostgreSQL | 0,00 % | 45,08 MiB |                1,15 % |
| Redis      | 0,75 % | 10,05 MiB |                0,26 % |
| MongoDB    | 0,66 % | 145,4 MiB |                3,71 % |

En esta prueba observamos que Redis fue el que menos memoria utilizó, mientras que MongoDB fue el que más consumió de los tres.

También vimos que el uso de CPU era bastante bajo en todos los contenedores.

Hay que tener en cuenta que estos resultados corresponden a una medición puntual, por lo que pueden cambiar dependiendo de las consultas que se estén realizando y de la carga de trabajo.

## 8. Uso de inteligencia artificial

1. Revisar una explicación más detallada del código a utilizar , como en el caso de los hilos en la medición de tiempos o la prueba de simultaniedad.

2. Contrastar errores que se han producido a la hora de crear código manualmente.

3. Generar código de ejemplo para poder aplicarlo a la hora de recoger datos por consola en reservas o razonar orden de ejecución.

4. Consultar dudas sobre el funcionamiento de PostgreSQL, MongoDB y Redis, especialmente para entender cómo realizar algunas consultas y comprobar los resultados.

5. Ayudarnos a comprender y completar algunas partes del código inicial proporcionado por el profesor, como el generador de datos `xera_datos.py`.

6. Resolver dudas durante la creación del script de copias de seguridad y comprobar cómo realizar las restauraciones de PostgreSQL y MongoDB.

7. Revisar errores que aparecieron durante las pruebas de la caché Redis, como la caducidad de las claves y su invalidación.

8. Ayudarnos a organizar y revisar la documentación del README, integrando las distintas partes del trabajo.
