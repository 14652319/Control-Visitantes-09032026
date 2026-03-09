-- =============================================
-- CONSULTAS SQL ÚTILES
-- Sistema de Control de Visitantes
-- =============================================

-- NOTA: Estas consultas son opcionales
-- El sistema funciona completamente sin necesidad de usar SQL directamente
-- Se proporcionan para administradores que quieran inspeccionar la BD

-- =============================================
-- CONEXIÓN A LA BASE DE DATOS
-- =============================================
-- Host: localhost
-- Puerto: 5432
-- Database: control_visitantes
-- Usuario: postgres
-- Password: G3st0radm$2025.


-- =============================================
-- CONSULTAS DE VERIFICACIÓN
-- =============================================

-- Ver todos los usuarios
SELECT 
    id,
    usuario,
    rol,
    estado,
    primer_nombre || ' ' || primer_apellido AS nombre_completo,
    dir_correo,
    sede_id,
    intentos_fallidos,
    ultimo_acceso
FROM usuarios
ORDER BY id;

-- Ver todas las sedes
SELECT * FROM sedes ORDER BY id;

-- Ver todas las dependencias con sus sedes
SELECT 
    d.id,
    d.prefijo_dependencia,
    d.descripcion_dependencia,
    d.estado,
    COUNT(sd.sede_id) as cantidad_sedes
FROM dependencias d
LEFT JOIN sede_dependencia sd ON d.id = sd.dependencia_id
GROUP BY d.id, d.prefijo_dependencia, d.descripcion_dependencia, d.estado
ORDER BY d.prefijo_dependencia;

-- Ver visitantes registrados
SELECT 
    id,
    tipo_identificacion,
    num_identificacion,
    primer_nombre || ' ' || primer_apellido AS nombre_completo,
    empresa,
    num_telefono,
    estado
FROM visitantes
ORDER BY id DESC
LIMIT 20;

-- Ver visitas de hoy
SELECT 
    lv.id,
    lv.fecha_ingreso,
    lv.hora_ingreso,
    lv.hora_salida,
    lv.num_identificacion,
    lv.primer_nombre || ' ' || lv.primer_apellido AS nombre_visitante,
    lv.empresa,
    lv.descripcion_dependencia,
    lv.estado_visita,
    lv.numero_carnet,
    s.descripcion_sede,
    u.usuario AS registrado_por
FROM log_visitantes lv
JOIN sedes s ON lv.sede_id = s.id
JOIN usuarios u ON lv.usuario_registro_id = u.id
WHERE lv.fecha_ingreso = CURRENT_DATE
ORDER BY lv.hora_ingreso DESC;

-- Ver visitantes actualmente en instalaciones
SELECT 
    lv.id,
    lv.hora_ingreso,
    lv.tipo_identificacion,
    lv.num_identificacion,
    lv.primer_nombre || ' ' || lv.primer_apellido AS nombre_visitante,
    lv.empresa,
    lv.descripcion_dependencia,
    lv.numero_carnet,
    s.descripcion_sede
FROM log_visitantes lv
JOIN sedes s ON lv.sede_id = s.id
WHERE lv.estado_visita = 'EN_INSTALACIONES'
  AND lv.fecha_ingreso = CURRENT_DATE
ORDER BY lv.hora_ingreso DESC;


-- =============================================
-- REPORTES Y ESTADÍSTICAS
-- =============================================

-- Estadísticas del día
SELECT 
    COUNT(*) as total_visitas,
    COUNT(CASE WHEN estado_visita = 'EN_INSTALACIONES' THEN 1 END) as en_instalaciones,
    COUNT(CASE WHEN estado_visita = 'SALIO' THEN 1 END) as salieron
FROM log_visitantes
WHERE fecha_ingreso = CURRENT_DATE;

-- Visitas por sede (últimos 30 días)
SELECT 
    s.descripcion_sede,
    COUNT(*) as total_visitas
FROM log_visitantes lv
JOIN sedes s ON lv.sede_id = s.id
WHERE lv.fecha_ingreso >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.descripcion_sede
ORDER BY total_visitas DESC;

-- Dependencias más visitadas (últimos 30 días)
SELECT 
    descripcion_dependencia,
    COUNT(*) as total_visitas
FROM log_visitantes
WHERE fecha_ingreso >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY descripcion_dependencia
ORDER BY total_visitas DESC
LIMIT 10;

-- Empresas que más visitan
SELECT 
    empresa,
    COUNT(*) as total_visitas,
    COUNT(DISTINCT num_identificacion) as visitantes_unicos
FROM log_visitantes
WHERE fecha_ingreso >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY empresa
ORDER BY total_visitas DESC
LIMIT 10;

-- Visitantes frecuentes
SELECT 
    v.tipo_identificacion,
    v.num_identificacion,
    v.primer_nombre || ' ' || v.primer_apellido AS nombre_completo,
    v.empresa,
    COUNT(*) as total_visitas
FROM visitantes v
JOIN log_visitantes lv ON v.num_identificacion = lv.num_identificacion
WHERE lv.fecha_ingreso >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY v.tipo_identificacion, v.num_identificacion, v.primer_nombre, v.primer_apellido, v.empresa
HAVING COUNT(*) > 1
ORDER BY total_visitas DESC;


-- =============================================
-- LOG DE EVENTOS (AUDITORÍA)
-- =============================================

-- Ver eventos recientes
SELECT 
    le.id,
    le.timestamp,
    le.tipo_evento,
    le.descripcion,
    le.usuario_nombre,
    le.nivel,
    le.ip_address
FROM log_eventos le
ORDER BY le.timestamp DESC
LIMIT 50;

-- Ver intentos de login fallidos
SELECT 
    timestamp,
    tipo_evento,
    descripcion,
    ip_address
FROM log_eventos
WHERE tipo_evento IN ('LOGIN_FALLIDO', 'USUARIO_BLOQUEADO')
ORDER BY timestamp DESC
LIMIT 20;

-- Ver actividad de un usuario específico
SELECT 
    timestamp,
    tipo_evento,
    descripcion,
    nivel
FROM log_eventos
WHERE usuario_nombre LIKE '%nombre%'
ORDER BY timestamp DESC;

-- Eventos por tipo (últimos 7 días)
SELECT 
    tipo_evento,
    COUNT(*) as cantidad,
    nivel
FROM log_eventos
WHERE fecha >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY tipo_evento, nivel
ORDER BY cantidad DESC;


-- =============================================
-- MANTENIMIENTO
-- =============================================

-- Desbloquear usuario
UPDATE usuarios
SET estado = 'ACTIVO',
    intentos_fallidos = 0,
    bloqueado_hasta = NULL
WHERE usuario = 'nombre_usuario';

-- Ver usuarios bloqueados
SELECT 
    usuario,
    primer_nombre || ' ' || primer_apellido AS nombre_completo,
    intentos_fallidos,
    bloqueado_hasta,
    ultimo_acceso
FROM usuarios
WHERE estado = 'BLOQUEADO';

-- Limpiar logs antiguos (más de 1 año)
-- PRECAUCIÓN: Esto eliminará datos permanentemente
-- DELETE FROM log_eventos WHERE fecha < CURRENT_DATE - INTERVAL '1 year';
-- DELETE FROM log_visitantes WHERE fecha_ingreso < CURRENT_DATE - INTERVAL '1 year';


-- =============================================
-- RESPALDOS Y EXPORTACIÓN
-- =============================================

-- Para hacer backup de la base de datos completa:
-- Desde línea de comandos (fuera de psql):
-- pg_dump -U postgres -d control_visitantes -f backup.sql

-- Para restaurar:
-- psql -U postgres -d control_visitantes -f backup.sql

-- Exportar visitas a CSV (desde psql con \copy):
-- \copy (SELECT * FROM log_visitantes WHERE fecha_ingreso >= CURRENT_DATE - INTERVAL '30 days') TO 'visitas.csv' CSV HEADER;


-- =============================================
-- INFORMACIÓN DEL SISTEMA
-- =============================================

-- Ver tamaño de las tablas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Contar registros en todas las tablas
SELECT 
    'usuarios' as tabla, COUNT(*) as registros FROM usuarios
UNION ALL
SELECT 'sedes', COUNT(*) FROM sedes
UNION ALL
SELECT 'dependencias', COUNT(*) FROM dependencias
UNION ALL
SELECT 'visitantes', COUNT(*) FROM visitantes
UNION ALL
SELECT 'log_visitantes', COUNT(*) FROM log_visitantes
UNION ALL
SELECT 'log_eventos', COUNT(*) FROM log_eventos;


-- =============================================
-- NOTAS IMPORTANTES
-- =============================================

/*
1. Estas consultas son para inspección y reporting manual
2. El sistema hace todo esto automáticamente a través de la API
3. NO modifiques directamente la BD en producción sin backup
4. Usa las consultas de DELETE con MUCHO cuidado
5. Para reportes regulares, usa la funcionalidad de exportación del sistema
*/
