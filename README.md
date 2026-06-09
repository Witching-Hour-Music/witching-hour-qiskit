# witching-hour-qiskit

`witching-hour-qiskit` is a small Python package that demonstrates the shortest practical path from a Qiskit circuit to a qBraid runtime job.

It is intentionally narrow:

- build a Bell-state circuit in Qiskit
- authenticate with qBraid
- inspect available devices
- submit a job through the qBraid runtime
- retrieve measurement counts

This repo is designed to be easy to review, easy to install into a qBraid custom environment, and easy to extend into a larger project later.

## What You Get

- A minimal installable package in `src/witching_hour_qiskit`
- A small public Python API
- A CLI for listing devices and submitting a Bell-state job
- A small FastAPI service for Witching Hour app integrations
- A runnable example in `examples/bell_state_job.py`
- Submission copy in `SUBMISSION.md`

## Requirements

- Python 3.10 or newer
- A qBraid account
- A valid qBraid API key in `QBRAID_API_KEY`
- Access to at least one runtime device in your qBraid account

## Install

Create and activate a virtual environment, then install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

If you do not need editable mode:

```bash
pip install .
```

The only runtime dependency is:

```text
qbraid[qiskit]>=0.11,<0.12
```

## Configure Credentials

Export your qBraid API key before running the package:

```bash
export QBRAID_API_KEY="your_api_key_here"
```

Get this value from the qBraid account portal, not from the raw auth flow:

1. Open `https://account.qbraid.com`
2. Sign in through the normal browser flow
3. Open the API key section in your account settings
4. Copy the API key shown there

If you land on a page asking for `idToken` or for `email` plus `refreshToken`, you are in the wrong flow for this package. This project expects a qBraid API key stored in `QBRAID_API_KEY`.

If you keep credentials in a local `.env` file, load them into the current shell before running commands:

```bash
set -a
source .env
set +a
```

## Quick Start

### 1. Verify authentication and device access

List the devices visible to your account:

```bash
witching-hour-qiskit list-devices --limit 5
```

You can also run the module directly:

```bash
python -m witching_hour_qiskit list-devices --limit 5
```

Expected output is a small list of qBraid runtime device objects. The exact values depend on your account and provider access.

### 2. Submit the Bell-state job

Run the included Bell-state example:

```bash
witching-hour-qiskit run-bell --device-id aws:aqt:qpu:ibex-q1 --shots 1000
```

Or use the example script:

```bash
python examples/bell_state_job.py
```

A successful run prints something like:

```text
Submitting circuit to aws:aqt:qpu:ibex-q1
Counts: {'00': 497, '11': 503}
```

The exact counts vary, but for an ideal Bell-state run you should expect most outcomes to be concentrated in `00` and `11`.

### 3. Run the API service

Start the local HTTP API:

```bash
witching-hour-qiskit serve-api --host 127.0.0.1 --port 8000
```

Or run it with uvicorn directly:

```bash
uvicorn witching_hour_qiskit.web:app --host 127.0.0.1 --port 8000
```

Then check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

## Python API

The package exposes three public helpers:

```python
from witching_hour_qiskit import (
    create_bell_state_circuit,
    list_devices,
    run_bell_state_job,
)

circuit = create_bell_state_circuit()
print(circuit.draw())

devices = list_devices(limit=5)
print(devices)

result = run_bell_state_job(
    device_id="aws:aqt:qpu:ibex-q1",
    shots=1000,
)
print(result.data.get_counts())
```

### `create_bell_state_circuit()`

Returns a two-qubit Bell-state circuit with measurements already attached.

### `list_devices(limit=10)`

Returns up to `limit` devices visible to the authenticated qBraid account.

### `run_bell_state_job(device_id=..., shots=...)`

Builds the Bell-state circuit, submits it to the requested qBraid runtime device, waits for completion, prints counts, and returns the runtime result object.

## CLI Reference

### `list-devices`

```bash
witching-hour-qiskit list-devices --limit 10
```

Arguments:

- `--limit`: maximum number of visible devices to print

### `run-bell`

```bash
witching-hour-qiskit run-bell --device-id aws:aqt:qpu:ibex-q1 --shots 1000
```

Arguments:

- `--device-id`: qBraid runtime device identifier
- `--shots`: number of shots to execute

### `serve-api`

```bash
witching-hour-qiskit serve-api --host 127.0.0.1 --port 8000
```

Arguments:

- `--host`: interface to bind the API server to
- `--port`: port for the API server

## HTTP API

The package now exposes a small FastAPI service that can be shared by `witching-hour-app`, `witching-hour-live`, and other Witching Hour clients.

### `GET /health`

Response:

```json
{"status": "ok"}
```

### `GET /devices?limit=5`

Response:

```json
{
  "count": 5,
  "devices": [
    "QbraidDevice('aws:aqt:qpu:ibex-q1')",
    "QbraidDevice('aws:quera:qpu:aquila')"
  ]
}
```

### `POST /run-bell`

Request:

```json
{
  "device_id": "aws:aqt:qpu:ibex-q1",
  "shots": 1000,
  "ritual_type": "bell",
  "user_id": "user-123",
  "wallet": "0x1234"
}
```

Response:

```json
{
  "job_id": "optional-qbraid-job-id",
  "device_id": "aws:aqt:qpu:ibex-q1",
  "shots": 1000,
  "counts": {"00": 497, "11": 503},
  "dominant_state": "11",
  "seed": "00:497|11:503",
  "ritual_outcome": "shadow-twin"
}
```

The `seed`, `dominant_state`, and `ritual_outcome` fields are intended for app-layer integrations like ritual outcomes, trait generation, live events, or collectible state transitions.

## Choosing a Device

The default device in the package is:

```text
aws:aqt:qpu:ibex-q1
```

That device may not be available to every account. Before running a job:

1. Use `list-devices` to see what your account can access.
2. Pick one valid device ID from that output.
3. Pass it through `--device-id` or `run_bell_state_job(device_id=...)`.

If you want to change the repo default, update `DEFAULT_DEVICE_ID` in `src/witching_hour_qiskit/api.py`.

## Example Workflow

The package performs this runtime flow:

1. Create a `QbraidProvider`
2. Resolve a target device by ID
3. Build a Bell-state circuit in Qiskit
4. Submit the circuit with a fixed shot count
5. Wait for completion
6. Print and return measurement counts

This is intentionally the smallest useful qBraid plus Qiskit workflow in the repository.

## Project Layout

```text
.
├── README.md
├── SUBMISSION.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── src
│   └── witching_hour_qiskit
│       ├── __init__.py
│       ├── __main__.py
│       ├── api.py
│       └── cli.py
└── examples
    └── bell_state_job.py
```

## qBraid Submission Positioning

This repo fits best as:

- application tooling
- research demo
- circuit building
- circuit manipulation
- provider integration

It does not currently implement:

- problem mapping
- advanced transpilation
- hardware-specific optimization
- domain-specific algorithms
- simulator infrastructure

## Troubleshooting

### `QBRAID_API_KEY` is missing

Set the environment variable before running the CLI or example:

```bash
export QBRAID_API_KEY="your_api_key_here"
```

### No devices are returned

Your account may not currently have runtime access to any devices, or your credentials may be invalid. Confirm the API key and check your qBraid account permissions.

### The default device ID fails

Not every qBraid account sees the same devices. Run:

```bash
witching-hour-qiskit list-devices --limit 20
```

Then rerun `run-bell` with a device ID that actually appears in your account output.

### Import or dependency errors

Make sure the package is installed in the active environment:

```bash
pip install -e .
```

## Publishing

Until a PyPI release exists, use the GitHub repository as the canonical package reference:

- Repository: <https://github.com/witchinghourartcollective/witching-hour-qiskit>
- Documentation: <https://github.com/witchinghourartcollective/witching-hour-qiskit#readme>

When you are ready to publish:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```
