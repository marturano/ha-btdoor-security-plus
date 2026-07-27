# OCR Pipeline

OCR accepts an image reference and returns normalized text blocks, language, confidence and optional bounding regions.

Sensitive identifiers must be redacted from logs. Cached OCR results require a content hash, bounded TTL and policy permission. OCR alone must not authorize security-sensitive actions.
