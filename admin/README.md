# SQL Antipattern Scanner - Admin Guide

This guide is for administrators and developers of the SQL Antipattern Scanner.

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/npiesco/sql-antipattern-scanner.git
   cd sql-antipattern-scanner
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package in editable mode with test dependencies:
   ```
   pip install -e .[test]
   ```

## Running Tests

To run the unit tests:

```
sql-antipattern-scanner --run-tests
```

## CLI Arguments

The SQL Antipattern Scanner accepts the following command-line arguments:

- `sql_file` (positional argument): Path to the SQL file to scan. Optional if `--query` option is used.
- `--query`: SQL query string to scan directly. If provided, `sql_file` argument is not required.
- `--format`: Output format for the report. Options: `json`, `csv`, `html`. Default: `json`.
- `--output`: Output file path for the report. If not provided, prints to console.
- `--run-tests`: Flag to run unit tests for SQL Antipattern Scanner.

General syntax:

```
sql-antipattern-scanner [sql_file] [--query QUERY] [--format FORMAT] [--output OUTPUT] [--run-tests]
```

Note: If both `sql_file` and `--query` are provided, the tool will prioritize the `--query` option.

## Building the Package

1. Ensure all tests pass.

2. Update the version number in `pyproject.toml`.

3. Build the package:
   ```
   python -m build
   ```

4. The built package will be in the `dist/` directory.

## Distributing the Package

1. Install twine if not already installed:
   ```
   pip install twine
   ```

2. Upload to PyPI:
   ```
   python -m twine upload dist/*
   ```

## Running the Tool Locally

When developing, you can run the tool using:

```
python -m sql_antipattern_scanner [arguments]
```

This allows you to test changes without reinstalling the package.

## Updating Documentation

Remember to update both this admin README and the public README when making changes to the tool's functionality or usage.

## License

SQL Antipattern Scanner is proprietary software. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

© 2024 Nicholas G. Piesco. All rights reserved.