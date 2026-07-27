# Resumen de arquitectura

Cada entrada de configuración posee un runtime de gateway aislado. Cloud, SIP/TLS, diálogo, multimedia, eventos, persistencia y diagnóstico normalizan el estado antes de que las entidades lo consuman. Las propiedades de entidad no realizan accesos de red.

Los servicios globales e intents Assist resuelven una entrada exacta antes de enviar comandos. El gateway físico es el dispositivo raíz; Cloud, SIP, llamadas, multimedia y diagnóstico son dispositivos lógicos. Alexa / Google Gate Bridge es un dispositivo virtual independiente sin `via_device`.

Los comandos requieren acción explícita, generan auditoría y no se reintentan a ciegas. Diagnóstico y Support Bundle usan saneado centralizado.
