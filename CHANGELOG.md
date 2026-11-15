# CHANGELOG

## [0.2.0] - 2025-11-11
### Added
- Processing Pipeline (ordered stages, shared context, async, error handling, cancellation support)
- Context Manager with request-scoped isolation and snapshots
- Decision Interface with DeterministicDecision baseline
- Module/Model Adapter interface and AdapterRegistry
- Resource Manager (CPU/memory info, limits, no GPU assumed)
- Simulated Sensor Module demo (software simulation only)
- Tests for v0.2 components
### Changed
- Updated public exports in shrp_ai.__init__
### Preserved
- All v0.1 functionality, public APIs, learning engine, tests (28/28 passing)
