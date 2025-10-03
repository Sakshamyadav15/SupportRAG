# Contributing to SupportRAG

Thank you for your interest in contributing to SupportRAG! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/SupportRAG.git
   cd SupportRAG
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Code Style

We follow PEP 8 and use automated tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run these before committing:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Testing

All new features should include tests. Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_embeddings.py
```

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for refactoring

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Areas for Contribution

- **New Features**: Multi-language support, caching, advanced search
- **Bug Fixes**: Report and fix issues
- **Documentation**: Improve guides, add examples
- **Tests**: Increase test coverage
- **Performance**: Optimize retrieval and generation

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing!
