.PHONY: pre
pre:
	@pre-commit run --all-files


.PHONY: sync
sync:
	@uv sync --all-extras --all-groups --all-packages -U
