# SQL Antipattern Scanner

SQL Antipattern Scanner is a command-line tool that scans SQL files/queries for antipatterns and generates a report in various formats.

## Installation

To install SQL Antipattern Scanner, navigate to the project root directory and run:

```
pip install -e .
```

This will install the package in editable mode, allowing you to make changes to the code and immediately see the effects.

## Usage

To use SQL Antipattern Scanner, run the following command:

```
python -m sql_antipattern_scanner.cli [arguments]
```

Available arguments are:

- `sql_file` (positional argument): Path to the SQL file to scan. Optional if `--query` option is used.

- `--query` (optional): SQL query string to scan directly. If provided, `sql_file` argument is not required.

- `--format` (optional): Output format for generated report. Supported values are `json`, `csv`, and `html`. Default is `json`.

- `--output` (optional): Output file path where report will be saved. If not provided, report will be printed to console.

- `--run-tests` (optional): Flag to run unit tests for SQL Antipattern Scanner. If provided, unit tests will be executed before scanning SQL code.

General syntax for running the script is:

```
python -m sql_antipattern_scanner.cli [sql_file] [--query QUERY] [--format FORMAT] [--output OUTPUT] [--run-tests]
```

Note: If both `sql_file` and `--query` are provided, script will prioritize `--query` option and scan provided query string only.

## Examples

*How to use SQL Antipattern Scanner*

1. Scan SQL file and print report to console:
   ```
   python -m sql_antipattern_scanner.cli sql_file.sql
   ```

2. Scan SQL query directly and save report to file in HTML format:
   ```
   python -m sql_antipattern_scanner.cli --query "SELECT * FROM users WHERE id = 1" --format html --output report.html
   ```

3. Scan SQL file and save report to file in CSV format:
   ```
   python -m sql_antipattern_scanner.cli sql_file.sql --format csv --output report.csv
   ```

4. Run unit tests and scan SQL file, saving report to file in JSON format (default):
   ```
   python -m sql_antipattern_scanner.cli sql_file.sql --run-tests --output report.json
   ```

5. Run unit tests only:
   ```
   python -m sql_antipattern_scanner.cli --run-tests
   ```

Note: JSON is default output format if `--format` option is not specified.