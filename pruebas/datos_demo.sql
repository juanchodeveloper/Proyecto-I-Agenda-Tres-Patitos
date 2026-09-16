-- Proyecto I - Agenda Digital "Tres Patitos"
-- Autor: Juan Pablo Picado Salas
-- Datos de demostracion para pruebas de interfaz y defensa.
-- Ejecutar despues de script.sql sobre una base agenda de prueba.

SET search_path TO prototipo, public;

TRUNCATE TABLE
    tareas,
    disponibilidades,
    participaciones,
    log_accesos,
    eventos,
    ubicaciones,
    categorias,
    usuario_telefonos,
    usuario_emails,
    usuarios
RESTART IDENTITY CASCADE;

INSERT INTO usuarios (nombre, apellido, activo) VALUES
('Ana', 'Soto', TRUE),
('Luis', 'Mora', TRUE),
('Carlos', 'Vega', TRUE),
('Marta', 'Rojas', FALSE);

INSERT INTO usuario_telefonos (id_usuario, telefono) VALUES
(1, '8888-1001'), (2, '8888-1002'), (3, '8888-1003');
INSERT INTO usuario_emails (id_usuario, email) VALUES
(1, 'ana.demo@agenda.local'),
(2, 'luis.demo@agenda.local'),
(3, 'carlos.demo@agenda.local');

INSERT INTO categorias (nombre, id_categoria_padre) VALUES
('Trabajo', NULL),
('Personal', NULL);
INSERT INTO categorias (nombre, id_categoria_padre) VALUES
('Reuniones', 1);

INSERT INTO ubicaciones (nombre, direccion, ciudad, capacidad) VALUES
('Sala A', 'Edificio Central, piso 1', 'Cartago', 20),
('Auditorio Principal', 'Edificio Central, piso 2', 'Cartago', 100),
('Sala Creativa', 'Edificio Innovacion, piso 1', 'Cartago', 12);

INSERT INTO eventos
(id_usuario_propietario, id_categoria, id_ubicacion, titulo, descripcion, fecha_inicio, fecha_fin)
VALUES
(1, 3, 1, 'Reunion historica', 'Evento previo para el historico de la ubicacion',
 (CURRENT_DATE - 1) + TIME '10:00', (CURRENT_DATE - 1) + TIME '11:00'),
(1, 3, 1, 'Reunion de proyecto', 'Revision de avances del proyecto',
 (CURRENT_DATE + 1) + TIME '09:00', (CURRENT_DATE + 1) + TIME '10:00'),
(2, 1, 2, 'Presentacion general', 'Presentacion del estado del equipo',
 (CURRENT_DATE + 1) + TIME '11:00', (CURRENT_DATE + 1) + TIME '12:00'),
(3, 3, 1, 'Taller interno', 'Taller de coordinacion',
 (CURRENT_DATE + 1) + TIME '15:00', (CURRENT_DATE + 1) + TIME '16:00');

INSERT INTO participaciones (id_evento, id_invitado, rol, estado_confirmacion)
VALUES (2, 2, 'Invitado', 'pendiente');

INSERT INTO log_accesos (id_usuario) VALUES (1), (2), (3);

INSERT INTO disponibilidades (id_usuario, fecha, hora_inicio, hora_fin, id_tipo_disponibilidad) VALUES
(1, CURRENT_DATE + 1, '08:00', '17:00', 1),
(2, CURRENT_DATE + 1, '08:00', '17:00', 1),
(3, CURRENT_DATE + 1, '08:00', '17:00', 1),
(3, CURRENT_DATE + 1, '14:00', '15:00', 3);

INSERT INTO tareas
(id_evento, id_usuario_responsable, titulo, descripcion, prioridad, fecha_limite, estado)
VALUES
(2, 2, 'Preparar minuta', 'Preparar minuta de la reunion de proyecto', 'Alta', CURRENT_DATE - 1, 'Pendiente'),
(2, 1, 'Enviar agenda', 'Compartir la agenda antes de la reunion', 'Media', CURRENT_DATE + 2, 'En progreso'),
(3, 3, 'Preparar diapositivas', 'Preparar material de la presentacion', 'Alta', CURRENT_DATE - 2, 'En progreso'),
(4, 1, 'Confirmar materiales', 'Revisar materiales del taller', 'Baja', CURRENT_DATE + 4, 'Pendiente'),
(3, 2, 'Reservar equipo', 'Equipo audiovisual confirmado', 'Media', CURRENT_DATE - 1, 'Completada');

SELECT 'usuarios' AS objeto, COUNT(*) AS filas FROM usuarios
UNION ALL SELECT 'ubicaciones', COUNT(*) FROM ubicaciones
UNION ALL SELECT 'eventos', COUNT(*) FROM eventos
UNION ALL SELECT 'disponibilidades', COUNT(*) FROM disponibilidades
UNION ALL SELECT 'tareas', COUNT(*) FROM tareas;
