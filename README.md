# Python Discord Code Jam 12 - Tubular Tulips

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installing uv

If you don't have uv installed, you can install it using:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/xerif-wenghoe/code-jam-12
   cd code-jam-12
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

This will create a virtual environment and install all project dependencies including development dependencies.

## Development

### Running Tests

Run the test suite using pytest:

```bash
uv run pytest
```

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

#### Linting

Check for linting issues:

```bash
uv run ruff check
```

Auto-fix linting issues where possible:

```bash
uv run ruff check --fix
```

#### Formatting

Format code:

```bash
uv run ruff format
```

Check if code is properly formatted:

```bash
uv run ruff format --check
```

### Pre-commit Hooks

This project comes with pre-configured pre-commit hooks for automatic code quality checks. The configuration includes:

- **Basic checks**: TOML/YAML validation, end-of-file fixing, trailing whitespace removal
- **Ruff**: Linting and formatting with `ruff-check` and `ruff-format`
- **Tests**: Automatic pytest execution before commits

To set up pre-commit hooks:

1. Install the pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

2. Run hooks on all files (optional):
   ```bash
   uv run pre-commit run --all-files
   ```

Now the hooks will run automatically on every commit, ensuring code quality and running tests.

### Adding Dependencies

Add a runtime dependency:

```bash
uv add <package-name>
```

Add a development dependency:

```bash
uv add --dev <package-name>
```

### Running the Server

This project includes a web server built with Starlette and Uvicorn that serves static files. To start the server:

```bash
uv run server.py
```

The server will start and be available at http://localhost:8000 by default.

## Configuration

The project configuration is managed in `pyproject.toml`:

- **Ruff**: Configured with comprehensive linting rules
- **Pytest**: Set up for testing with development dependencies
- **Python**: Requires Python 3.13+

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and linting: `uv run pytest && uv run ruff check`
5. Test the server: `uv run -m cj12`
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).
