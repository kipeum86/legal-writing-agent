# Private Documents (Opaque Directory)

Everything under `docs/_private/` is gitignored by a wildcard rule. Agents load files from this directory at runtime; external observers see only the directory name, not the file list.

Do NOT add references to specific filenames from this directory in any other committed file. Agent-facing loaders should use local configuration values so private filenames stay local.

For filenames that must stay fully private, store them outside the repo and load via an environment variable, following the existing private-directory configuration pattern.
