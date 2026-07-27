# Target Evidence Sanitization Guide

## Remove before import

- access tokens, passwords and API keys;
- SIP usernames, passwords, certificates and private keys;
- public or internal URLs beyond a non-identifying host label;
- exact MAC addresses, serial numbers, entry IDs and device IDs unless hashed;
- names, addresses, camera images, audio and visitor information;
- cookies, authorization headers and complete HTTP request dumps.

## Keep

- Home Assistant version and installation type;
- integration version;
- elapsed times, memory measurements and result status;
- redacted log messages with timestamps and component names;
- entity counts and generalized availability results;
- screenshots with sensitive fields obscured.

## Recommended replacements

Use stable placeholders such as:

- `<HA_HOST>`
- `<CONFIG_ENTRY_ID>`
- `<DEVICE_ID>`
- `<SERIAL_REDACTED>`
- `<TOKEN_REDACTED>`

Evidence must remain understandable after redaction. If redaction makes a result unverifiable, repeat the test with a purpose-built sanitized capture instead of importing sensitive data.
