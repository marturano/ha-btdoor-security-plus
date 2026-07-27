# Security Certification

The automated security certification performs repository-local checks for likely committed secrets, unsafe logging patterns, unpinned dependencies and risky subprocess/shell usage. Results require human review and do not replace deployment threat-model validation.

Final certification additionally requires validation on the target Home Assistant installation, including redaction of diagnostics, credential handling, network exposure and supply-chain review.
