# Strict Typing Audit

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Current gate

`pyproject.toml` currently enables selected mypy checks:

```toml
[tool.mypy]
python_version = "3.13"
check_untyped_defs = true
warn_unused_ignores = true
warn_redundant_casts = true
no_implicit_optional = true
exclude = ["tests"]
```

It does not enable strict mode and no repository-local mypy executable is available in the validation environment. Therefore a strict pass cannot be claimed.

## Measured static baseline

- 77 Python modules;
- 65 unannotated parameters;
- 94 functions without explicit return annotations;
- 172 AST `Any` references;
- 210 textual `Any` occurrences;
- `BticinoConfigEntry = ConfigEntry[Any]`;
- no `type: ignore` debt;
- no `cast(...)` debt.

These numbers are indicators, not direct mypy error counts.

## Highest-priority files

### `sensor.py`

Largest annotation gap. Many entity properties use compact one-line definitions without explicit return types. Refactor mechanically in small groups and preserve entity behaviour.

### `__init__.py`

Replace `ConfigEntry[Any]` with `ConfigEntry[BTDoorRuntimeData]`. Ensure all setup, unload, update, diagnostics, service, and platform signatures use the alias.

### `developer.py` and support models

Replace broad `dict[str, Any]` payloads with TypedDicts, dataclasses, enums, or Protocols for diagnostic results, support bundle sections, and test outputs.

### Runtime provider and event bus

Replace `Any` entry/runtime inputs with Protocols or concrete runtime types. Type listener callbacks and exported dictionaries.

### `cloud.py`

Type parsed JSON boundaries explicitly. Use aliases/TypedDicts for API payloads while keeping validation at untrusted boundaries.

## Required strict gate

A Platinum implementation should add an executable CI command equivalent to:

```bash
mypy --strict custom_components/btdoor_security_plus
```

Expected configuration topics:

- `strict = true`;
- no untyped definitions;
- no untyped decorators;
- disallow `Any` propagation where practical;
- warn unreachable;
- strict equality;
- explicit package bases;
- concrete typed config entry;
- typed external dependency with `py.typed`.

Tests may remain outside the Platinum source gate initially, but production code must pass without broad per-module suppression.

## Completion criteria

1. Repeatable mypy installation and lock/pin in CI.
2. Strict pass on all integration modules.
3. Concrete typed config entry used throughout.
4. External library publishes `py.typed`.
5. No blanket ignores or module-wide suppression.
6. Type gate included in governance and release workflow.
