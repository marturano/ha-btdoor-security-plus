# Estrategia de pruebas

La validación combina compilación Python, análisis JSON/YAML, HACS, hassfest, regresiones dirigidas y pruebas runtime Home Assistant 2026.x. Los escenarios incluyen instalación limpia, actualización, configuración, recarga, descarga, reinicio y varias entradas.

Las pruebas de registro verifican duplicados y conservación de IDs, nombres, áreas y estado deshabilitado. Las pruebas de seguridad garantizan que las rutas automáticas no abran la puerta y que una entrada no controle otro gateway.

Asistentes, saneado, exportaciones privadas, paneles y recursos Assist son controles independientes. La evidencia real se registra por separado.
