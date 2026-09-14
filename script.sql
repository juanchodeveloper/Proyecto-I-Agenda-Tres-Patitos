-- Proyecto 1 - Agenda Digital "Tres Patitos"
-- Script consolidado para PostgreSQL 18+
-- IMPORTANTE: crear previamente una base de datos llamada agenda y ejecutar este
-- archivo conectado a esa base. El script reconstruye el esquema prototipo.

DROP SCHEMA IF EXISTS prototipo CASCADE;
CREATE SCHEMA prototipo;
SET search_path TO prototipo, public;

-- ============================================================
-- 1. NUCLEO BASE
-- ============================================================

-- RF01
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- RF02, RE02, RN02
CREATE TABLE usuario_telefonos (
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    telefono VARCHAR(20) NOT NULL,
    PRIMARY KEY (id_usuario, telefono)
);

CREATE TABLE usuario_emails (
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    email VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_usuario, email)
);

-- RF03, RE05, RN04
CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    id_categoria_padre INTEGER REFERENCES categorias(id_categoria)
);

-- ============================================================
-- 2. MODULO A - GESTION DE UBICACIONES (RF08-RF10)
-- ============================================================

CREATE TABLE ubicaciones (
    id_ubicacion SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    capacidad INTEGER NOT NULL,
    CONSTRAINT check_ubicacion_capacidad CHECK (capacidad > 0)
);

-- RF04, RE04 + RF09
CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    id_usuario_propietario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_categoria INTEGER NOT NULL REFERENCES categorias(id_categoria),
    id_ubicacion INTEGER NOT NULL REFERENCES ubicaciones(id_ubicacion),
    titulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    CONSTRAINT check_evento_fechas CHECK (fecha_fin > fecha_inicio)
);

-- RF05, RE01, RN01, RN05
CREATE TABLE participaciones (
    id_evento INTEGER NOT NULL REFERENCES eventos(id_evento) ON DELETE CASCADE,
    id_invitado INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    rol VARCHAR(50),
    estado_confirmacion VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    CONSTRAINT check_estado_confirmacion
        CHECK (estado_confirmacion IN ('aceptado', 'pendiente', 'rechazado')),
    PRIMARY KEY (id_evento, id_invitado)
);

-- RF06
CREATE TABLE log_accesos (
    id_log SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    fecha_acceso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. MODULO B - DISPONIBILIDAD Y GESTION DE TIEMPOS (RF11-RF12)
-- ============================================================

CREATE TABLE tipos_disponibilidad (
    id_tipo_disponibilidad SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO tipos_disponibilidad (nombre)
VALUES ('disponible'), ('ocupado'), ('no disponible');

CREATE TABLE disponibilidades (
    id_disponibilidad SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    id_tipo_disponibilidad INTEGER NOT NULL
        REFERENCES tipos_disponibilidad(id_tipo_disponibilidad),
    CONSTRAINT check_disponibilidad_horas CHECK (hora_fin > hora_inicio)
);

-- ============================================================
-- 4. MODULO D - TAREAS ASOCIADAS A EVENTOS (RF15-RF17)
-- ============================================================

-- La prioridad se conserva como texto obligatorio porque el enunciado no define
-- un catálogo ni un conjunto cerrado de valores para este atributo.
CREATE TABLE tareas (
    id_tarea SERIAL PRIMARY KEY,
    id_evento INTEGER NOT NULL REFERENCES eventos(id_evento),
    id_usuario_responsable INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    titulo VARCHAR(120) NOT NULL,
    descripcion TEXT,
    prioridad VARCHAR(30) NOT NULL,
    fecha_limite DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    CONSTRAINT check_tarea_estado
        CHECK (estado IN ('Pendiente', 'En progreso', 'Completada', 'Cancelada'))
);

-- ============================================================
-- 5. INDICES JUSTIFICADOS POR CONSULTAS DE LOS RF SELECCIONADOS
-- ============================================================

-- RF09: deteccion de conflictos por recinto y rango temporal.
CREATE INDEX idx_eventos_ubicacion_fechas
    ON eventos (id_ubicacion, fecha_inicio, fecha_fin);

-- RF12: busqueda de disponibilidad por usuario, fecha e intervalo.
CREATE INDEX idx_disponibilidades_usuario_fecha_horas
    ON disponibilidades (id_usuario, fecha, hora_inicio, hora_fin);

-- RF16-RF17: pendientes y carga de trabajo por responsable, estado y vencimiento.
CREATE INDEX idx_tareas_responsable_estado_fecha
    ON tareas (id_usuario_responsable, estado, fecha_limite);

-- ============================================================
-- 6. FUNCIONES Y TRIGGERS DE INTEGRIDAD
-- ============================================================

-- RE05: evita tanto autorreferencia directa como ciclos indirectos.
CREATE OR REPLACE FUNCTION evitar_ciclo_categorias()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id_categoria_padre IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.id_categoria_padre = NEW.id_categoria THEN
        RAISE EXCEPTION 'Una categoria no puede ser padre de si misma.';
    END IF;

    IF EXISTS (
        WITH RECURSIVE ancestros AS (
            SELECT c.id_categoria, c.id_categoria_padre
            FROM categorias c
            WHERE c.id_categoria = NEW.id_categoria_padre

            UNION

            SELECT c.id_categoria, c.id_categoria_padre
            FROM categorias c
            JOIN ancestros a
              ON c.id_categoria = a.id_categoria_padre
        )
        SELECT 1
        FROM ancestros
        WHERE id_categoria = NEW.id_categoria
    ) THEN
        RAISE EXCEPTION 'La relacion propuesta genera un ciclo en la jerarquia de categorias.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_evitar_ciclo
BEFORE INSERT OR UPDATE OF id_categoria_padre ON categorias
FOR EACH ROW
EXECUTE FUNCTION evitar_ciclo_categorias();

-- RE04: una FK garantiza existencia, pero no que el propietario este activo.
CREATE OR REPLACE FUNCTION validar_propietario_activo()
RETURNS TRIGGER AS $$
DECLARE
    v_activo BOOLEAN;
BEGIN
    SELECT activo
      INTO v_activo
      FROM usuarios
     WHERE id_usuario = NEW.id_usuario_propietario;

    IF v_activo IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'El propietario del evento debe existir y estar activo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_propietario_activo
BEFORE INSERT OR UPDATE OF id_usuario_propietario ON eventos
FOR EACH ROW
EXECUTE FUNCTION validar_propietario_activo();

-- RF09: intervalos tratados como [inicio, fin). Que un evento termine justo
-- cuando otro comienza NO constituye traslape.
CREATE OR REPLACE FUNCTION evitar_traslape_ubicacion()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
          FROM eventos e
         WHERE e.id_ubicacion = NEW.id_ubicacion
           AND e.id_evento <> COALESCE(NEW.id_evento, -1)
           AND NEW.fecha_inicio < e.fecha_fin
           AND e.fecha_inicio < NEW.fecha_fin
    ) THEN
        RAISE EXCEPTION 'La ubicacion ya tiene un evento que se traslapa con el rango indicado.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_evitar_traslape_ubicacion
BEFORE INSERT OR UPDATE OF id_ubicacion, fecha_inicio, fecha_fin ON eventos
FOR EACH ROW
EXECUTE FUNCTION evitar_traslape_ubicacion();

-- ============================================================
-- 7. VISTAS Y CONSULTAS ANALITICAS
-- ============================================================

-- RF07 / RE03 / RN03: antiguedad calculada, no almacenada.
CREATE VIEW vista_antiguedad_usuarios AS
SELECT
    id_usuario,
    nombre,
    apellido,
    fecha_registro,
    age(CURRENT_DATE, fecha_registro) AS antiguedad
FROM usuarios;

-- RF07 / RE03: duracion diaria calculada, no almacenada.
CREATE VIEW vista_duracion_eventos_diarios AS
SELECT
    id_usuario_propietario,
    fecha_inicio::DATE AS dia,
    SUM(EXTRACT(EPOCH FROM (fecha_fin - fecha_inicio)) / 60.0) AS duracion_total_minutos
FROM eventos
GROUP BY id_usuario_propietario, fecha_inicio::DATE;

-- RF10: ranking dinamico por volumen de eventos.
CREATE VIEW vista_ocupacion_ubicaciones AS
SELECT
    u.id_ubicacion,
    u.nombre,
    u.ciudad,
    u.capacidad,
    COUNT(e.id_evento) AS total_eventos,
    COUNT(e.id_evento) FILTER (WHERE e.fecha_inicio >= CURRENT_TIMESTAMP) AS eventos_programados,
    COUNT(e.id_evento) FILTER (WHERE e.fecha_inicio < CURRENT_TIMESTAMP) AS eventos_historicos
FROM ubicaciones u
LEFT JOIN eventos e ON e.id_ubicacion = u.id_ubicacion
GROUP BY u.id_ubicacion, u.nombre, u.ciudad, u.capacidad;

-- RF16: eventos que mantienen tareas activas vencidas.
CREATE VIEW vista_eventos_tareas_vencidas AS
SELECT
    e.id_evento,
    e.titulo AS evento,
    COUNT(t.id_tarea) AS tareas_vencidas
FROM eventos e
JOIN tareas t ON t.id_evento = e.id_evento
WHERE t.fecha_limite < CURRENT_DATE
  AND t.estado IN ('Pendiente', 'En progreso')
GROUP BY e.id_evento, e.titulo;

-- RF16-RF17: pendientes y carga de trabajo cuantitativa por usuario.
CREATE VIEW vista_carga_trabajo AS
SELECT
    u.id_usuario,
    u.nombre,
    u.apellido,
    COUNT(t.id_tarea) FILTER (
        WHERE t.estado IN ('Pendiente', 'En progreso')
    ) AS tareas_activas,
    COUNT(t.id_tarea) FILTER (
        WHERE t.estado = 'Pendiente'
    ) AS pendientes,
    COUNT(t.id_tarea) FILTER (
        WHERE t.estado = 'En progreso'
    ) AS en_progreso,
    COUNT(t.id_tarea) FILTER (
        WHERE t.fecha_limite < CURRENT_DATE
          AND t.estado IN ('Pendiente', 'En progreso')
    ) AS vencidas
FROM usuarios u
LEFT JOIN tareas t ON t.id_usuario_responsable = u.id_usuario
GROUP BY u.id_usuario, u.nombre, u.apellido;

-- RF12: usuarios activos que declararon disponibilidad que cubre por completo
-- el rango, no tienen una franja bloqueante y no tienen un evento traslapado
-- como propietarios ni como invitados.
CREATE OR REPLACE FUNCTION usuarios_disponibles(
    p_fecha DATE,
    p_hora_inicio TIME,
    p_hora_fin TIME
)
RETURNS TABLE (
    id_usuario INTEGER,
    nombre VARCHAR,
    apellido VARCHAR
) AS $$
BEGIN
    IF p_hora_fin <= p_hora_inicio THEN
        RAISE EXCEPTION 'La hora final debe ser posterior a la hora inicial.';
    END IF;

    RETURN QUERY
    SELECT u.id_usuario, u.nombre, u.apellido
      FROM usuarios u
     WHERE u.activo = TRUE
       AND EXISTS (
            SELECT 1
              FROM disponibilidades d
              JOIN tipos_disponibilidad td
                ON td.id_tipo_disponibilidad = d.id_tipo_disponibilidad
             WHERE d.id_usuario = u.id_usuario
               AND d.fecha = p_fecha
               AND td.nombre = 'disponible'
               AND d.hora_inicio <= p_hora_inicio
               AND d.hora_fin >= p_hora_fin
       )
       AND NOT EXISTS (
            SELECT 1
              FROM disponibilidades d
              JOIN tipos_disponibilidad td
                ON td.id_tipo_disponibilidad = d.id_tipo_disponibilidad
             WHERE d.id_usuario = u.id_usuario
               AND d.fecha = p_fecha
               AND td.nombre IN ('ocupado', 'no disponible')
               AND p_hora_inicio < d.hora_fin
               AND d.hora_inicio < p_hora_fin
       )
       AND NOT EXISTS (
            SELECT 1
              FROM eventos e
             WHERE (e.id_usuario_propietario = u.id_usuario
                    OR EXISTS (
                        SELECT 1
                          FROM participaciones p
                         WHERE p.id_evento = e.id_evento
                           AND p.id_invitado = u.id_usuario
                           AND p.estado_confirmacion <> 'rechazado'
                    ))
               AND (p_fecha + p_hora_inicio) < e.fecha_fin
               AND e.fecha_inicio < (p_fecha + p_hora_fin)
       )
     ORDER BY u.nombre, u.apellido;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================
-- 8. VERIFICACIONES DE ESTRUCTURA (solo lectura)
-- ============================================================

-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'prototipo' ORDER BY table_name;
-- SELECT * FROM vista_ocupacion_ubicaciones ORDER BY total_eventos DESC, nombre;
-- SELECT * FROM vista_carga_trabajo ORDER BY tareas_activas DESC, vencidas DESC;
