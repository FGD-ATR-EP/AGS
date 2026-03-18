# Dependency Inventory and Role Separation

This inventory compares the legacy flat `requirements.txt` package list against the current Python import graph under `src/` and maps each dependency to a clearer role.

## Survey method

- Parsed direct Python imports in `src/`.
- Compared imported top-level modules to the packages previously listed in the root `requirements.txt`.
- Kept runtime packages only where there is a verifiable import or where the package is required to support declared runtime configuration loading.

## Required runtime

These packages are imported by the canonical runtime path and are now kept in `requirements/base.txt` and `requirements/runtime.txt`.

| Package | Evidence from `src/` | Role |
| --- | --- | --- |
| `fastapi` | API / WebSocket ingress in `src/backend/main.py` | HTTP + WebSocket ingress |
| `uvicorn` | Runtime launcher imports in `src/backend/main.py` | ASGI serving |
| `pydantic` | Envelope, entropy, and model schemas across `src/backend/genesis_core/` | Schema validation |
| `pydantic-settings` | `src/backend/core/config.py` | Environment-driven config |
| `python-dotenv` | Required by `SettingsConfigDict(env_file=".env")` local env loading path | Local `.env` support |
| `requests` | Marketing/search adapters | Sync HTTP client |
| `httpx` | Auth/provider and service HTTP clients | Async/sync HTTP client |
| `itsdangerous` | Session/auth signing | Signing primitives |
| `pyzmq` | `src/backend/genesis_core/bus/tachyon.py` | Internal ZeroMQ Tachyon transport |
| `websockets` | `src/backend/genesis_core/bus/tachyon.py` | External bridge client/server support |
| `uvloop` | Runtime event loop optimization | Event loop acceleration |
| `msgpack` | Bus serialization in `src/backend/genesis_core/bus/base.py` | Canonical binary codec |
| `orjson` | Bus serialization in `src/backend/genesis_core/bus/base.py` | Fast JSON codec |
| `numpy` | Presentation / visual processing paths | Numeric runtime utility |

## Optional ML / visual dependencies

These packages are imported only by optional AI, vision, or advanced embedding paths and are now isolated in `requirements/optional-ml-visual.txt`.

| Package | Evidence from `src/` | Role |
| --- | --- | --- |
| `google-generativeai` | Gemini adapters in `src/backend/genesis_core/logenesis/` | Managed model provider |
| `Pillow` | Image processing and Gemini image input helpers | Visual preprocessing |
| `torch` | Vision core, region extraction, tensor-backed models | Heavy ML runtime |
| `scipy` | Reserved for advanced numerical/visual work; kept as optional ML support | Numeric extension |
| `diffusers` | Test harness already mocks it as optional | Image/video generation experimentation |
| `transformers` | Test harness already mocks it as optional | Transformer model support |
| `accelerate` | Test harness already mocks it as optional | Accelerator/runtime helper |
| `sentence-transformers` | Optional import in `src/backend/genesis_core/auditorium/dual_architecture.py` | Embedding-based alignment audit |

## Development / test dependencies

These packages are not required by the production runtime and are now isolated in `requirements/dev.txt`.

| Package | Evidence | Role |
| --- | --- | --- |
| `pytest` | Imported throughout `tests/` | Test runner |

## Packages pruned from the runtime manifest

The following packages were present in the legacy flat manifest but have no verified direct import in `src/` today, so they were removed from the default runtime install path.

| Package | Rationale |
| --- | --- |
| `colorama` | No import in `src/` or required test path. |
| `PyJWT[crypto]` | No direct JWT import in `src/`; auth currently relies on session/signing flows instead. |
| `nats-py` | No current NATS client import; Tachyon/ZeroMQ is the active canonical bus path. |

## Install strategy

- `pip install -r requirements.txt` → canonical runtime only.
- `pip install -r requirements/optional-ml-visual.txt` → add optional ML/visual capabilities.
- `pip install -r requirements/dev.txt` → full local development + tests.

## Notes

- Optional packages remain available for future phases, but isolating them keeps the core AI-OS runtime smaller and easier to validate.
- This split aligns with the platform direction: keep the canonical bus/governance/memory path lightweight, while advanced inference and visual workloads remain opt-in.
