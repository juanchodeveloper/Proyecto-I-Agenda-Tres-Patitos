# Checklist de cierre del Proyecto I - Agenda Digital Tres Patitos

Este archivo controla lo que falta para cerrar la entrega sin omitir ningún requisito evaluable.

## 1. Repositorio y control de versiones

- [x] Repositorio público creado.
- [x] Rama principal `main` disponible.
- [x] README, script SQL, aplicación Python, dependencias, modelos, pruebas e informe incorporados.
- [x] Historial inicial de commits estructurados.
- [ ] Registrar mediante commits reales la validación, correcciones, evidencias y documentación final.
- [ ] Verificar al final que el enlace público funcione sin iniciar sesión.

## 2. Restauración PostgreSQL

- [ ] Confirmar PostgreSQL 18 o superior.
- [ ] Crear base de datos vacía `agenda`.
- [ ] Ejecutar `script.sql` conectado a `agenda`.
- [ ] Confirmar esquema `prototipo`.
- [ ] Confirmar tablas del núcleo y de los módulos seleccionados.
- [ ] Confirmar vistas analíticas.
- [ ] Confirmar funciones y triggers críticos.
- [ ] Ejecutar validación rápida de solo lectura.

## 3. Puesta en marcha Python

- [ ] Confirmar Python 3.10 o superior.
- [ ] Instalar `requirements.txt`.
- [ ] Ajustar `DB_CONFIG` únicamente si cambian usuario, contraseña, host o puerto.
- [ ] Ejecutar `agenda.py`.
- [ ] Confirmar conexión correcta a PostgreSQL.
- [ ] Confirmar pestañas Usuarios, Categorías, Eventos, Ubicaciones, Disponibilidad y Tareas.

## 4. Validación funcional

### Ubicaciones RF08-RF10
- [ ] CRUD de ubicaciones.
- [ ] Evento asociado a ubicación.
- [ ] Histórico/agenda por ubicación.
- [ ] Prevención de traslape en mismo recinto.
- [ ] Ranking de uso/demanda.

### Disponibilidad RF11-RF12
- [ ] CRUD de franjas de disponibilidad.
- [ ] Tipos disponible, ocupado y no disponible.
- [ ] Consulta de usuarios disponibles en rango horario.
- [ ] Cruce correcto entre disponibilidad declarada y eventos existentes.

### Tareas RF15-RF17
- [ ] CRUD de tareas.
- [ ] Estados Pendiente, En progreso, Completada y Cancelada.
- [ ] Reporte de tareas/eventos vencidos.
- [ ] Reporte de carga de trabajo por usuario.

### Integridad base relevante
- [ ] RE04: impedir propietario inactivo.
- [ ] RE05: impedir ciclos indirectos de categorías.
- [ ] RE02: impedir contacto duplicado por usuario.
- [ ] RN01: cascada de participaciones al eliminar evento.

## 5. Evidencias visuales obligatorias

Las capturas finales deben provenir de la aplicación conectada a PostgreSQL y deben explicarse en el informe.

- [ ] E01 - RF08 CRUD de ubicaciones.
- [ ] E02 - RF09 evento asociado a una ubicación.
- [ ] E03 - RF09 rechazo por traslape.
- [ ] E04 - RF10 ranking de ubicaciones.
- [ ] E05 - RF11 CRUD de disponibilidad.
- [ ] E06 - RF12 usuarios disponibles.
- [ ] E07 - RF15 CRUD de tareas.
- [ ] E08 - RF16 tareas/eventos vencidos.
- [ ] E09 - RF17 carga de trabajo por usuario.

Evidencias técnicas adicionales recomendadas:

- [ ] T01 - ejecución limpia de `script.sql` y esquema `prototipo` visible.
- [ ] T02 - aplicación abierta y conectada correctamente.
- [ ] T03 - prueba RE04 o RE05 si aporta claridad al informe/defensa.

## 6. Informe final

- [ ] Completar integrantes, profesora y fecha.
- [ ] Mantener la selección explícita de Ubicaciones, Disponibilidad y Tareas.
- [ ] Indicar que RF13-RF14 no fueron seleccionados.
- [ ] Insertar evidencias reales con pie de figura y explicación.
- [ ] Relacionar cada evidencia con sus RF correspondientes.
- [ ] Actualizar la matriz de trazabilidad según resultados realmente verificados.
- [ ] Revisar modelos conceptual, lógico y físico dentro del informe.
- [ ] Revisar coherencia entre informe, SQL, Python y repositorio.
- [ ] Generar versión final DOCX/PDF si la entrega lo requiere.

## 7. Defensa presencial

- [ ] Practicar restauración limpia desde el repositorio.
- [ ] Practicar configuración de conexión y arranque de Python.
- [ ] Practicar demostración de los tres módulos seleccionados.
- [ ] Practicar explicación de triggers, FK, traslapes, disponibilidad y reportes.
- [ ] Mantener la demostración dentro de 15 minutos.

## 8. Entrega

- [ ] Revisión final contra instrucciones y rúbrica.
- [ ] Repositorio público actualizado.
- [ ] Informe final actualizado.
- [ ] Evidencias reales incluidas.
- [ ] Enlace público entregado en TecDigital.

## Registro de capturas recibidas

| ID | Archivo/captura | Qué demuestra | RF/Regla | Estado |
|---|---|---|---|---|
| T01 | Pendiente | Restauración limpia y estructura creada | Implementación | Pendiente |
| T02 | Pendiente | Aplicación conectada | Integración GUI-BD | Pendiente |
| E01 | Pendiente | CRUD de ubicaciones | RF08 | Pendiente |
| E02 | Pendiente | Evento con ubicación | RF09 | Pendiente |
| E03 | Pendiente | Rechazo de traslape | RF09 | Pendiente |
| E04 | Pendiente | Ranking de espacios | RF10 | Pendiente |
| E05 | Pendiente | CRUD de disponibilidad | RF11 | Pendiente |
| E06 | Pendiente | Usuarios disponibles | RF12 | Pendiente |
| E07 | Pendiente | CRUD de tareas | RF15 | Pendiente |
| E08 | Pendiente | Vencimientos | RF16 | Pendiente |
| E09 | Pendiente | Carga de trabajo | RF17 | Pendiente |
