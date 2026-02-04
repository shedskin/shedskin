
.PHONY: all sync build rebuild test lint format typecheck qa clean \
        distclean wheel sdist dist check publish-test publish upgrade \
        coverage coverage-html docs release help

# Default target
all: build

# Sync environment (initial setup, installs dependencies + package)
sync:
	@uv sync

# Build/rebuild the extension after code changes
build:
	@uv sync --reinstall-package shedskin

# Alias for build
rebuild: build

# Run tests
test:
	@uv run pytest tests/ -v

# Lint with ruff
lint:
	@uv run ruff check --exclude shedskin/lib --fix shedskin/

# Format with ruff
format:
	@uv run ruff format --exclude shedskin/lib shedskin/

# Type check with mypy
typecheck:
	@uv run mypy --strict shedskin/ --exclude '.venv' --exclude shedskin/lib

# Run a full quality assurance check
qa: test lint typecheck format

# Build wheel
wheel:
	@uv build --wheel

# Build source distribution
sdist:
	@uv build --sdist

# Check distributions with twine
check:
	@uv run twine check dist/*

# Build both wheel and sdist
dist: wheel sdist check

# Publish to TestPyPI
publish-test: check
	@uv run twine upload --repository testpypi dist/*

# Publish to PyPI
publish: check
	@uv run twine upload dist/*

# Upgrade all dependencies
upgrade:
	@uv lock --upgrade
	@uv sync

# Run tests with coverage
coverage:
	@uv run pytest tests/ -v --cov=shedskin --cov-report=term-missing

# Generate HTML coverage report
coverage-html:
	@uv run pytest tests/ -v --cov=shedskin --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# Build documentation (requires sphinx in dev dependencies)
docs:
	@uv run sphinx-build -b html docs/ docs/_build/html

# Create a release (bump version, tag, push)
release:
	@echo "Current version: $$(grep '^version' pyproject.toml | head -1)"
	@read -p "New version: " version; 	sed -i '' "s/^version = .*/version = \"$$version\"/" pyproject.toml; 	git add pyproject.toml; 	git commit -m "Bump version to $$version"; 	git tag -a "v$$version" -m "Release $$version"; 	echo "Tagged v$$version. Run 'git push && git push --tags' to publish."

# Clean build artifacts
clean:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf src/*.egg-info/
	@rm -rf .pytest_cache/
	@find . -name "*.so" -delete
	@find . -name "*.pyd" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Clean everything including CMake cache
distclean: clean
	@rm -rf CMakeCache.txt CMakeFiles/

# Show help
help:
	@echo "Available targets:"
	@echo "  all          - Build/rebuild the extension (default)"
	@echo "  sync         - Sync environment (initial setup)"
	@echo "  build        - Rebuild extension after code changes"
	@echo "  rebuild      - Alias for build"
	@echo "  test         - Run tests"
	@echo "  lint         - Lint with ruff"
	@echo "  format       - Format with ruff"
	@echo "  typecheck    - Type check with mypy"
	@echo "  qa           - Run full quality assurance (test, lint, typecheck, format)"
	@echo "  wheel        - Build wheel distribution"
	@echo "  sdist        - Build source distribution"
	@echo "  dist         - Build both wheel and sdist"
	@echo "  check        - Check distributions with twine"
	@echo "  publish-test - Publish to TestPyPI"
	@echo "  publish      - Publish to PyPI"
	@echo "  upgrade      - Upgrade all dependencies"
	@echo "  coverage     - Run tests with coverage"
	@echo "  coverage-html- Generate HTML coverage report"
	@echo "  docs         - Build documentation with Sphinx"
	@echo "  release      - Bump version, tag, and prepare release"
	@echo "  clean        - Remove build artifacts"
	@echo "  distclean    - Remove all generated files"
	@echo "  help         - Show this help message"
