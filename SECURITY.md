# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| main    | ✅        |

## Security Notes

### python-ecdsa Minerva timing side-channel

The `python-ecdsa` project has a known timing side-channel issue (Minerva-style) affecting operations that rely on secret nonces/scalars (for example signing and ECDH on P-256). Signature verification is not affected.

Because the upstream `python-ecdsa` project does not plan to harden this class of side-channel in scope, this repository avoids relying on `python-ecdsa` in runtime dependencies.

Mitigation in this repository:
- `python-jose` was removed from runtime dependencies to avoid pulling `python-ecdsa`.
- JWT functionality should use `PyJWT[crypto]` (OpenSSL-backed `cryptography`) instead of pure-Python ECDSA stacks for production signing operations.

## Reporting a Vulnerability

Please open a private security report (or issue marked `security`) with:
- impact summary,
- reproducible steps,
- affected files/modules,
- and suggested remediation if available.

We will acknowledge within 72 hours and provide a remediation plan or risk-acceptance rationale.
