# Health Score

The Health Score is a deterministic, provider-weighted summary of runtime condition. Each provider returns a bounded score from 0 to 100, duration, timeout information, issues and a human-readable explanation. A failing or timed-out provider is isolated so the remaining diagnostics can still be collected.

The aggregate score is the weighted average of valid provider scores. Negative weights are ignored. Status thresholds are: `healthy` 95–100, `degraded` 70–94 and `unhealthy` 0–69. Provider severity follows the same bands; a timeout is critical.

Entity properties only read normalized runtime state. They never perform network or file operations. Detailed evidence belongs in diagnostics and the private Support Bundle.
