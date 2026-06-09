# qBraid Submission Draft

Use this file as source copy for a qBraid publish request or repository description.

## Project name

`witching-hour-qiskit`

## Short description

A minimal qBraid plus Qiskit starter package for authenticating, discovering runtime devices, and submitting a simple Bell-state circuit through the qBraid runtime.

## Repository URL

https://github.com/witchinghourartcollective/witching-hour-qiskit

## What users can do with it

- Authenticate with qBraid using an account API key
- List runtime devices visible to their account
- Build a small Bell-state circuit in Qiskit
- Submit that circuit through qBraid and retrieve counts
- Use the repo as a minimal starting point for larger qBraid workflows

## Primary audience

Developers who want the smallest possible qBraid plus Qiskit example that still exercises a real runtime submission flow.

## Why it belongs in the ecosystem

This repository gives new users a low-friction starting point for the qBraid ecosystem with a narrow dependency set, a documented setup flow, an installable package, and a runnable end-to-end Qiskit example.

## Scope statement

This repository is intentionally minimal. It focuses on the qBraid-to-Qiskit runtime path and does not currently include advanced transpilation, domain-specific workflows, simulator tooling, or provider-specific optimization layers.

## Suggested submission sentence

Please consider `witching-hour-qiskit` for inclusion in the qBraid ecosystem as a minimal Qiskit-based starter environment that helps users authenticate, inspect available devices, and submit their first runtime job with very little setup overhead.

## Maintainer notes

- Keep `README.md` aligned with the actual package behavior and defaults.
- Replace the example device ID if your account uses a different accessible backend.
- Keep `requirements.txt` and `pyproject.toml` in sync.
- Make sure the repository is public before submitting it for review.
