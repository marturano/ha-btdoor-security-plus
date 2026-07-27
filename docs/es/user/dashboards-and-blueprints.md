# Paneles y blueprints

Usa el gestor de paneles para resolver los tokens con la entrada seleccionada. Importa el YAML generado, no la plantilla original, y verifica todas las entidades antes de activar acciones.

La tarjeta de la puerta debe llamar a `button.press` sobre `button.apri_cancello` con confirmación. No uses el antiguo modelo `cover` ni `cover.open_cover`. Los marcadores antiguos compatibles se mantienen para paneles guardados; los nuevos deben usar entidades actuales.

El panel operativo puede incluir Cloud, SIP, llamadas, multimedia y el resumen de la última llamada. Developer Console debe permanecer privada. El blueprint histórico de caducidad necesita todavía un sensor de días restantes y no es un flujo 1.1 completo.
