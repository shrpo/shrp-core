# SHRP Core v0.2

## Purpose
SHRP Core is a reusable, hardware-independent software foundation that can be imported as a Python library or run as a standalone local service. The same Core implementation powers both modes.

**Current version:** v0.2

## Architecture
See `docs/ARCHITECTURE.md` and `docs/PROJECT_AUDIT.md`

## Components
- **Core Engine** — initialization, lifecycle, coordination
- **Module Manager** — registration, lookup, dispatch, lifecycle
- **Pipeline** — ordered processing stages with shared context
- **Context Manager** — request-scoped isolated execution context
- **Decision Interface** — structured decision output
- **Adapter System** — model/module adapter registry
- **Resource Manager** — CPU/memory awareness (no GPU assumption)
- **State Manager** — controlled shared state with snapshots
- **Memory Manager** — SQLite-backed persistent storage
- **Event System** — async event bus with subscriber isolation
- **Task Manager** — async task submission, cancellation, timeouts
- **API Layer** — FastAPI endpoints for Standalone Mode

## Installation
```bash
# Use existing venv
F:\Ai\SHRP_AI\.venv\Scripts\activate
pip install -r requirements.txt
```

## Dependencies
- **Core:** Python 3.11+, asyncio
- **Standalone:** FastAPI, Uvicorn, Pydantic v2+
- **Learning engine:** NumPy, scipy, matplotlib, pytest, psutil

## Library Mode
```python
from shrp_ai import CoreEngine, Request
import asyncio

async def main():
    core = CoreEngine()
    await core.initialize()
    resp = await core.handle_request(Request('1', 'echo', {'hello': 'world'}))
    print(resp.status, resp.result)
    await core.shutdown()

asyncio.run(main())
```

## Standalone Mode
```bash
uvicorn shrp_ai.api.app:app --host 127.0.0.1 --port 8000
```

Endpoints:
- `GET /health`
- `GET /v1/status`
- `GET /v1/modules`
- `POST /v1/requests`

## Module Development
Implement `BaseModule` with `name`, `version`, `description`, `initialize()`, `execute(payload)`, `shutdown()`. Register with `core.modules`.

## Testing
```bash
$env:PYTHONPATH='F:\Ai\SHRP_AI\src'; .\.venv\Scripts\python.exe -m pytest -v
```

## Current Limitations
- CPU-only, no GPU required
- Local-only by default (127.0.0.1)
- Learning engine separate from core (optional module)
- DeterministicDecision is a baseline, not a reasoning system
- SimulatedSensorModule is a software simulation only

## Project Structure
```
SHRP_AI/
├── src/shrp_ai/
│   ├── core/          # Engine, modules, state, memory, events, tasks, runtime
│   ├── pipeline/      # Ordered processing stages
│   ├── context/       # Request-scoped context manager
│   ├── decision/      # Decision interface and baseline
│   ├── adapters/      # Module/model adapter registry
│   ├── resources/     # CPU/memory resource manager
│   ├── modules_demo/  # Simulated sensor demo module
│   ├── api/           # FastAPI application
│   ├── nn/            # Learning engine (NumPy)
│   ├── training/      # Trainer, optimizers
│   ├── inference/     # Inference engine
│   ├── multitask/     # Multi-task model
│   ├── config/        # Configuration system
│   ├── memory/        # Memory monitoring
│   └── utils/         # Checkpoints, tensor utils
├── tests/
├── examples/
├── docs/
└── experiments/
```

## Existing Learning Engine
Preserved under `src/shrp_ai/nn`, `training`, `inference`, `multitask`. See `docs/PHASE_2_1_LEARNING_ENGINE.md`.

## Verification
See `docs/SHRP_CORE_V0_2_VERIFICATION.md` for full HTTP integration test results.