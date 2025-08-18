.PHONY: build
build:
	@docker build -t cj12-tubular-tulips .

.PHONY: run
run:
	@docker run --name cj12 -d -p 8000:8000 cj12-tubular-tulips

.PHONY: pre
pre:
	@pre-commit run --all-files

.PHONY: sync
sync:
	@uv sync --all-extras --all-groups --all-packages -U
