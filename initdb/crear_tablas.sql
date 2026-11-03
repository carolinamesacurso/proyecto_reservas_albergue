-- =====================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS: GESTIÓN DE ALBERGUES (PostgreSQL)
-- =====================================================================

CREATE TABLE IF NOT EXISTS PEREGRINOS (
    id_peregrino SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    documento_identidad VARCHAR(30) NOT NULL UNIQUE,
    fecha_nacimiento DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS ALBERGUES (
    id_albergue SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    camino VARCHAR(200) NOT NULL,
    concello VARCHAR(200) NOT NULL,
    plazas INT NOT NULL,
    precio REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS RESERVAS (
    id_reserva SERIAL PRIMARY KEY,
    id_peregrino INT NOT NULL,
    id_albergue INT NOT NULL,
    fecha_desde DATE NOT NULL,
    dias INT NOT NULL,
    CONSTRAINT fk_reserva_peregrino FOREIGN KEY (id_peregrino) REFERENCES PEREGRINOS(id_peregrino) ON DELETE CASCADE,
    CONSTRAINT fk_reserva_albergue FOREIGN KEY (id_albergue) REFERENCES ALBERGUES(id_albergue) ON DELETE CASCADE
);