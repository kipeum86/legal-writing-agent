# Private Documents (Opaque Directory)

Everything under `docs/_private/` is gitignored by a wildcard rule. Agents load files from this directory at runtime; external observers see only the directory name, not the file list.

Do NOT add references to specific filenames from this directory in any other committed file if the filename itself is sensitive. Agent-facing loaders must still name the file, and that is acceptable — the tradeoff is that the filename is exposed at the loader site but not in `.gitignore` or in directory listings.

For filenames that must stay fully secret, store them outside the repo and load via an environment variable (see the `CONTRACT_REVIEW_PRIVATE_DIR` / `LEGAL_AGENT_PRIVATE_DIR` pattern introduced in Task 7 of the security-hardening plan).
