# SQL Antipattern Scanner

SQL Antipattern Scanner is a powerful tool that scans SQL files/queries for antipatterns and generates comprehensive reports in various formats.

## Installation

To install SQL Antipattern Scanner, simply run:

```
pip install sql-antipattern-scanner
```

## Usage

After installation, you can use SQL Antipattern Scanner from the command line:

```
sql-antipattern-scanner [arguments]
```

Available arguments are:

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

## Examples

1. Scan SQL file and print report to console:
   ```
   sql-antipattern-scanner path/to/your/sql_file.sql
   ```

2. Scan SQL query and save report in HTML format:
   ```
   sql-antipattern-scanner --query "SELECT * FROM users WHERE id = 1" --format html --output report.html
   ```

3. Scan SQL file and save report in CSV format:
   ```
   sql-antipattern-scanner path/to/your/sql_file.sql --format csv --output report.csv
   ```

4. Run unit tests and scan SQL file, saving report in JSON format:
   ```
   sql-antipattern-scanner path/to/your/sql_file.sql --run-tests --output report.json
   ```

5. Run unit tests only:
   ```
   sql-antipattern-scanner --run-tests
   ```

## Features

- Detects a wide range of SQL antipatterns
- Generates detailed reports with severity levels and suggestions for improvement
- Supports multiple output formats for easy integration into your workflow
- Fast and efficient scanning of large SQL files
- Includes comprehensive unit tests to ensure reliability

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

© 2024 Nicholas G. Piesco. All rights reserved.