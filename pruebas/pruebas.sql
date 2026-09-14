-- Bateria de pruebas del Proyecto 1
-- Ejecutar sobre una restauracion limpia para evitar datos duplicados de una corrida anterior.
-- Ejecutar DESPUES de script.sql, conectado a la BD agenda.
-- IMPORTANTE: algunas sentencias estan disenadas para FALLAR y comprobar restricciones.

SET search_path TO prototipo, public;

-- ============================================================
-- DATOS BASE PARA PRUEBAS
-- ============================================================
INSERT INTO usuarios (nombre, apellido, activo) VALUES
('Ana', 'Soto', TRUE),
('Luis', 'Mora', TRUE),
('Marta', 'Rojas', FALSE);

INSERT INTO categorias (nombre) VALUES ('Trabajo'), ('Personal');
INSERT INTO categorias (nombre, id_categoria_padre)
SELECT 'Reuniones', id_categoria FROM categorias WHERE nombre='Trabajo';

INSERT INTO ubicaciones (nombre, direccion, ciudad, capacidad) VALUES
('Sala A', 'Edificio Central, piso 1', 'Cartago', 20),
('Auditorio', 'Edificio Central, piso 2', 'Cartago', 100);

-- ============================================================
-- RE05 - CICLOS
-- ============================================================
-- POSITIVO: jerarquia valida.
UPDATE categorias
SET id_categoria_padre = (SELECT id_categoria FROM categorias WHERE nombre='Personal')
WHERE nombre='Trabajo';

-- NEGATIVO: debe FALLAR por ciclo indirecto.
-- UPDATE categorias
-- SET id_categoria_padre = (SELECT id_categoria FROM categorias WHERE nombre='Reuniones')
-- WHERE nombre='Personal';

-- ============================================================
-- RE04 / RF09 - EVENTOS Y PROPIETARIO ACTIVO
-- ============================================================
-- POSITIVO: evento valido.
INSERT INTO eventos (
    id_usuario_propietario, id_categoria, id_ubicacion,
    titulo, descripcion, fecha_inicio, fecha_fin
)
SELECT u.id_usuario, c.id_categoria, ub.id_ubicacion,
       'Reunion inicial', 'Prueba de evento',
       '2026-10-10 09:00', '2026-10-10 10:00'
FROM usuarios u, categorias c, ubicaciones ub
WHERE u.nombre='Ana' AND c.nombre='Trabajo' AND ub.nombre='Sala A';

-- LIMITE: debe permitir iniciar exactamente cuando termina el anterior.
INSERT INTO eventos (
    id_usuario_propietario, id_categoria, id_ubicacion,
    titulo, fecha_inicio, fecha_fin
)
SELECT u.id_usuario, c.id_categoria, ub.id_ubicacion,
       'Reunion consecutiva', '2026-10-10 10:00', '2026-10-10 11:00'
FROM usuarios u, categorias c, ubicaciones ub
WHERE u.nombre='Luis' AND c.nombre='Trabajo' AND ub.nombre='Sala A';

-- NEGATIVO RF09: debe FALLAR por traslape en Sala A. Descomentar para probar.
-- INSERT INTO eventos (
--     id_usuario_propietario, id_categoria, id_ubicacion,
--     titulo, descripcion, fecha_inicio, fecha_fin
-- )
-- SELECT u.id_usuario, c.id_categoria, ub.id_ubicacion,
--        'Evento en conflicto', 'Debe ser rechazado',
--        '2026-10-10 09:30', '2026-10-10 10:30'
-- FROM usuarios u, categorias c, ubicaciones ub
-- WHERE u.nombre='Ana' AND c.nombre='Trabajo' AND ub.nombre='Sala A';

-- NEGATIVO RE04: debe FALLAR porque Marta esta inactiva. Descomentar para probar.
-- INSERT INTO eventos (
--     id_usuario_propietario, id_categoria, id_ubicacion,
--     titulo, descripcion, fecha_inicio, fecha_fin
-- )
-- SELECT u.id_usuario, c.id_categoria, ub.id_ubicacion,
--        'Evento propietario inactivo', 'Debe ser rechazado',
--        '2026-10-11 09:00', '2026-10-11 10:00'
-- FROM usuarios u, categorias c, ubicaciones ub
-- WHERE u.nombre='Marta' AND c.nombre='Trabajo' AND ub.nombre='Auditorio';

-- ============================================================
-- RF11-RF12 - DISPONIBILIDAD
-- ============================================================
INSERT INTO disponibilidades (id_usuario, fecha, hora_inicio, hora_fin, id_tipo_disponibilidad)
SELECT u.id_usuario, '2026-10-10', '08:00', '12:00', td.id_tipo_disponibilidad
FROM usuarios u, tipos_disponibilidad td
WHERE u.nombre='Ana' AND td.nombre='disponible';

INSERT INTO disponibilidades (id_usuario, fecha, hora_inicio, hora_fin, id_tipo_disponibilidad)
SELECT u.id_usuario, '2026-10-10', '08:00', '12:00', td.id_tipo_disponibilidad
FROM usuarios u, tipos_disponibilidad td
WHERE u.nombre='Luis' AND td.nombre='disponible';

-- Ana y Luis tienen eventos entre 09:00 y 11:00; para 11:00-12:00 ambos deberian
-- quedar disponibles si no existen otros compromisos.
SELECT * FROM usuarios_disponibles('2026-10-10', '11:00', '12:00');

-- Para 09:30-09:45, Ana debe quedar excluida por el evento 09:00-10:00 y Luis
-- puede quedar disponible si su evento inicia exactamente a las 10:00.
SELECT * FROM usuarios_disponibles('2026-10-10', '09:30', '09:45');

-- NEGATIVO: debe FALLAR por rango invertido.
-- SELECT * FROM usuarios_disponibles('2026-10-10', '16:00', '14:00');

-- ============================================================
-- RF15-RF17 - TAREAS
-- ============================================================
INSERT INTO tareas (
    id_evento, id_usuario_responsable, titulo, descripcion,
    prioridad, fecha_limite, estado
)
SELECT e.id_evento, u.id_usuario, 'Preparar minuta', 'Documento previo a la reunion',
       'Alta', CURRENT_DATE - 1, 'Pendiente'
FROM eventos e, usuarios u
WHERE e.titulo='Reunion inicial' AND u.nombre='Luis';

INSERT INTO tareas (
    id_evento, id_usuario_responsable, titulo,
    prioridad, fecha_limite, estado
)
SELECT e.id_evento, u.id_usuario, 'Enviar convocatoria',
       'Media', CURRENT_DATE + 5, 'En progreso'
FROM eventos e, usuarios u
WHERE e.titulo='Reunion inicial' AND u.nombre='Ana';

SELECT * FROM vista_eventos_tareas_vencidas;
-- RF16: la columna pendientes responde la cantidad de tareas pendientes por usuario.
-- RF17: activas, pendientes, en progreso y vencidas permiten revisar carga de trabajo.
SELECT * FROM vista_carga_trabajo ORDER BY tareas_activas DESC, vencidas DESC;
SELECT * FROM vista_ocupacion_ubicaciones ORDER BY total_eventos DESC;

-- NEGATIVO RF15: debe FALLAR por estado fuera del conjunto oficial. Descomentar.
-- INSERT INTO tareas (
--     id_evento, id_usuario_responsable, titulo, prioridad, fecha_limite, estado
-- )
-- SELECT e.id_evento, u.id_usuario, 'Estado invalido', 'Baja', CURRENT_DATE, 'Terminada'
-- FROM eventos e, usuarios u
-- WHERE e.titulo='Reunion inicial' AND u.nombre='Ana';

-- NEGATIVO RF11: debe FALLAR por hora final anterior al inicio.
-- INSERT INTO disponibilidades (id_usuario, fecha, hora_inicio, hora_fin, id_tipo_disponibilidad)
-- SELECT u.id_usuario, '2026-10-12', '18:00', '17:00', td.id_tipo_disponibilidad
-- FROM usuarios u, tipos_disponibilidad td
-- WHERE u.nombre='Ana' AND td.nombre='disponible';

-- NEGATIVO de integridad referencial: tarea con evento inexistente.
-- INSERT INTO tareas (id_evento, id_usuario_responsable, titulo, prioridad, fecha_limite, estado)
-- SELECT 999999, u.id_usuario, 'Evento inexistente', 'Baja', CURRENT_DATE, 'Pendiente'
-- FROM usuarios u WHERE u.nombre='Ana';

-- RE02: duplicado de telefono para un mismo usuario debe FALLAR en el segundo INSERT.
-- INSERT INTO usuario_telefonos (id_usuario, telefono)
-- SELECT id_usuario, '8888-8888' FROM usuarios WHERE nombre='Ana';
-- INSERT INTO usuario_telefonos (id_usuario, telefono)
-- SELECT id_usuario, '8888-8888' FROM usuarios WHERE nombre='Ana';
