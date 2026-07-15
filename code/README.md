# Executable verifier

`severance_audit_verifier.py` is a verbatim extraction of the Python program in Appendix A.7 of the paper.

It constructs:

- the primary capacity witness with profile `(1, 1.0)`;
- an edge-removal example with profile `(1, 0.0)`;
- a same-verdict capacity example with profile `(0, 1.0)`.

Run:

```bash
python severance_audit_verifier.py
```

The program uses only the Python standard library and exits non-zero if any declared invariant fails.
