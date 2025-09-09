# Contributing to PyObComp

Thank you for your interest in contributing to PyObComp! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/pyobcomp.git
   cd pyobcomp
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Use **black** for code formatting: `black src/ tests/`
- Use **flake8** for linting: `flake8 src/ tests/`

## Testing

- Write tests for all new functionality
- Ensure all tests pass: `pytest`
- Aim for high test coverage
- Use descriptive test names that explain what is being tested

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for your changes

4. **Run the test suite**:
   ```bash
   pytest
   ```

5. **Commit your changes** with clear, descriptive commit messages

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots or examples if applicable

## Issue Reporting

When reporting issues, please include:

- **Python version** and operating system
- **PyObComp version**
- **Minimal reproducible example**
- **Expected vs actual behavior**
- **Error messages** (if any)

## Feature Requests

For feature requests, please:

- Check if the feature already exists or is planned
- Provide a clear use case and motivation
- Consider if the feature fits the project's scope
- Be open to discussion and alternative approaches

## Code Review

All submissions require review. We look for:

- **Correctness**: Does the code work as intended?
- **Style**: Does it follow project conventions?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Are there any performance implications?

## Release Process

Releases are managed by maintainers. The process includes:

1. Version bumping
2. Changelog updates
3. Tag creation
4. PyPI package upload

## Questions?

Feel free to open an issue for questions about contributing or the project in general.

Thank you for contributing to PyObComp! 🎉
