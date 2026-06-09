"""Minimal qBraid and Qiskit helper functions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import os
from pathlib import Path
import tempfile
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_TMPDIR = PROJECT_ROOT / ".tmp"


def ensure_tempdir() -> None:
    """Provide a writable temp directory before importing heavy deps."""
    current_tmpdir = os.getenv("TMPDIR")
    if current_tmpdir:
        try:
            candidate = Path(current_tmpdir)
            candidate.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=candidate):
                return
        except OSError:
            pass

    PROJECT_TMPDIR.mkdir(parents=True, exist_ok=True)
    os.environ["TMPDIR"] = str(PROJECT_TMPDIR)
    tempfile.tempdir = str(PROJECT_TMPDIR)


ensure_tempdir()

from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

DEFAULT_DEVICE_ID = "aws:aqt:qpu:ibex-q1"
DEFAULT_SHOTS = 1000


def ensure_qbraid_api_key() -> None:
    """Load QBRAID_API_KEY from a local .env file when possible."""
    if os.getenv("QBRAID_API_KEY"):
        return

    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        if key.strip() == "QBRAID_API_KEY":
            os.environ.setdefault("QBRAID_API_KEY", value.strip().strip('"').strip("'"))
            return


def create_bell_state_circuit() -> QuantumCircuit:
    """Create a 2-qubit Bell-state circuit with measurement."""
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    return circuit


def list_devices(limit: int = 10) -> Sequence[object]:
    """Return a small list of devices visible to the current qBraid account."""
    ensure_qbraid_api_key()
    provider = QbraidProvider()
    return provider.get_devices()[:limit]


def serialize_devices(limit: int = 10) -> list[str]:
    """Return visible qBraid devices as strings for JSON responses."""
    return [str(device) for device in list_devices(limit=limit)]


def summarize_counts(counts: Mapping[str, Any]) -> dict[str, Any]:
    """Convert raw counts into stable app-facing fields."""
    normalized_counts = {str(key): int(value) for key, value in counts.items()}
    dominant_state = max(
        normalized_counts,
        key=normalized_counts.get,
        default=None,
    )
    seed = "|".join(
        f"{state}:{normalized_counts[state]}" for state in sorted(normalized_counts)
    )

    ritual_map = {
        "00": "ember-gate",
        "01": "mirror-signal",
        "10": "veil-strike",
        "11": "shadow-twin",
    }

    return {
        "counts": normalized_counts,
        "dominant_state": dominant_state,
        "seed": seed,
        "ritual_outcome": ritual_map.get(dominant_state, "unknown-ritual"),
    }


def run_bell_state_job_summary(
    device_id: str = DEFAULT_DEVICE_ID,
    shots: int = DEFAULT_SHOTS,
) -> dict[str, Any]:
    """Run the Bell-state circuit and return a JSON-safe summary."""
    ensure_qbraid_api_key()
    provider = QbraidProvider()
    device = provider.get_device(device_id)
    circuit = create_bell_state_circuit()

    job = device.run(circuit, shots=shots)
    result = job.result()
    counts = result.data.get_counts()

    return {
        "job_id": getattr(job, "id", None),
        "device_id": device_id,
        "shots": shots,
        **summarize_counts(counts),
    }


def run_bell_state_job(
    device_id: str = DEFAULT_DEVICE_ID,
    shots: int = DEFAULT_SHOTS,
) -> object:
    """Submit the Bell-state circuit to a qBraid runtime device and return the result."""
    ensure_qbraid_api_key()
    provider = QbraidProvider()
    device = provider.get_device(device_id)
    circuit = create_bell_state_circuit()

    print(f"Submitting circuit to {device_id}")
    job = device.run(circuit, shots=shots)
    result = job.result()
    print("Counts:", result.data.get_counts())
    return result
