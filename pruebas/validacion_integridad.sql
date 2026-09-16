-- Proyecto I - Agenda Digital "Tres Patitos"
-- Autor: Juan Pablo Picado Salas
-- Validacion controlada de RE04 y RE05.

SET search_path TO prototipo, public;

DROP TABLE IF EXISTS resultados_integridad;
CREATE TEMP TABLE resultados_integridad (
    prueba VARCHAR(10),
    resultado TEXT
);

DO $$
DECLARE
    v_usuario_inactivo INTEGER;
    v_categoria INTEGER;
    v_ubicacion INTEGER;
BEGIN
    SELECT id_usuario INTO v_usuario_inactivo
    FROM usuarios
    WHERE activo = FALSE
    LIMIT 1;

    SELECT id_categoria INTO v_categoria FROM categorias LIMIT 1;
    SELECT id_ubicacion INTO v_ubicacion FROM ubicaciones LIMIT 1;

    BEGIN
        INSERT INTO eventos (
            id_usuario_propietario, id_categoria, id_ubicacion,
            titulo, descripcion, fecha_inicio, fecha_fin
        ) VALUES (
            v_usuario_inactivo, v_categoria, v_ubicacion,
            'Prueba RE04', 'Debe rechazarse por propietario inactivo',
            '2099-01-01 09:00', '2099-01-01 10:00'
        );
        INSERT INTO resultados_integridad VALUES ('RE04', 'ERROR: permitio propietario inactivo');
    EXCEPTION WHEN OTHERS THEN
        INSERT INTO resultados_integridad VALUES ('RE04', 'OK: ' || SQLERRM);
    END;
END $$;

DO $$
DECLARE
    v_a INTEGER;
    v_b INTEGER;
BEGIN
    INSERT INTO categorias(nombre) VALUES ('TEST_CICLO_A') RETURNING id_categoria INTO v_a;
    INSERT INTO categorias(nombre, id_categoria_padre) VALUES ('TEST_CICLO_B', v_a) RETURNING id_categoria INTO v_b;

    BEGIN
        UPDATE categorias SET id_categoria_padre = v_b WHERE id_categoria = v_a;
        INSERT INTO resultados_integridad VALUES ('RE05', 'ERROR: permitio ciclo indirecto');
    EXCEPTION WHEN OTHERS THEN
        INSERT INTO resultados_integridad VALUES ('RE05', 'OK: ' || SQLERRM);
    END;

    DELETE FROM categorias WHERE id_categoria = v_b;
    DELETE FROM categorias WHERE id_categoria = v_a;
END $$;

SELECT * FROM resultados_integridad ORDER BY prueba;
