# ARCHITECTURE — SHRP Core v0.1

## Overview
SHRP Core is a reusable, hardware-independent software foundation that can be imported as a Python library or run as a standalone local service. Both modes share the same Core implementation.

## Target Components (Logical Responsibilities)

### 1. Core Engine
- **Purpose:** System initialization, lifecycle management, coordination
- **Responsibilities:** start/stop, component orchestration, health/status, failure handling
- **Dependencies:** All other components
- **Location:** src/shrp_ai/core/engine.py

### 2. Module Manager
- **Purpose:** Formal module contract and lifecycle
- **Responsibilities:** registration, lookup, enable/disable, dispatch, duplicate protection
- **Interface:** name, version, description, initialize(), execute(payload), shutdown()
- **Location:** src/shrp_ai/core/modules.py

### 3. Input/Output Interfaces
- **Purpose:** Validated request/response models
- **Models:** Request(request_id, module, payload), Response(request_id, status, result, error)
- **Location:** src/shrp_ai/core/interfaces.py

### 4. State Manager
- **Purpose:** Controlled shared state
- **Operations:** get/set/delete/clear/snapshots
- **Location:** src/shrp_ai/core/state.py

### 5. Memory Manager
- **Purpose:** Persistent JSON-compatible storage
- **Backend:** SQLite with parameterized queries
- **Operations:** save/get/delete/list
- **Location:** src/shrp_ai/core/memory.py

### 6. Event System
- **Purpose:** Async event bus
- **Features:** publish/subscribe, multiple subscribers, error isolation
- **Location:** src/shrp_ai/core/events.py

### 7. Task Manager
- **Purpose:** Async task execution
- **Features:** submit, status tracking, cancellation, timeouts, limits, graceful shutdown
- **Location:** src/shrp_ai/core/tasks.py

### 8. Runtime Manager
- **Purpose:** Mode management
- **Modes:** Library Mode (direct import), Standalone Mode (FastAPI)
- **Location:** src/shrp_ai/core/runtime.py

### 9. API Layer
- **Purpose:** HTTP interface for Standalone Mode
- **Framework:** FastAPI + Uvicorn
- **Endpoints:** GET /health, GET /v1/status, GET /v1/modules, POST /v1/requests
- **Binding:** 127.0.0.1:8000 by default
- **Location:** src/shrp_ai/api/app.py

### 10. Diagnostics and Logging
- **Purpose:** Structured logging, error tracking, status
- **Features:** Component status, no sensitive payload logging by default
- **Location:** src/shrp_ai/core/diagnostics.py

### 11. Configuration System
- **Purpose:** TOML-based configuration
- **Location:** src/shrp_ai/config/core_config.py (extends existing config)

## Communication Flow
1. Request arrives (Library API or HTTP) -> validated by I/O interfaces
2. Core Engine routes to Module Manager
3. Module Manager dispatches to registered module
4. Modules may use State/Memory/Event/Task services
5. Response returned through same path
6. Events published asynchronously for side effects

## Design Principles
- Reuse existing components where appropriate
- Keep learning engine separate from core
- Both modes use same Core implementation
- No external AI services, no GPU required
- Local-only by default
- Minimal dependencies
