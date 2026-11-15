# CHANGELOG

## [0.2.0] - 2025-11-15
### Added
- Processing Pipeline, Context Manager, Decision Interface, Adapter Registry, Resource Manager, Simulated Sensor Module
- Standalone Mode with FastAPI and Uvicorn
- 28 tests passing

## [0.3.0] - 2025-11-15
### Added
- Performance baseline benchmarks (7 components measured)
- 13 reliability tests (concurrent requests, task cancellation, event isolation, memory stability, etc.)
### Changed
- SQLite MemoryManager: persistent connection instead of per-operation open/close
- TaskManager: automatic task cleanup, max task limit enforcement
- CoreEngine.shutdown(): proper task awaiting and SQLite connection cleanup
### Fixed
- Memory leak in TaskManager (completed tasks never removed)
- SQLite connection leak on shutdown
### Preserved
- All v0.2 functionality and public APIs
- All existing tests (28/28 continue to pass)
- Learning engine untouched