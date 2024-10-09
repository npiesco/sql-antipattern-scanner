# sql-antipattern-scanner/sql_antipattern_scanner/cli.py
import argparse
from sql_antipattern_scanner import SQLAntipatternScanner
from test_sql_antipattern_scanner import run_tests

def main():
    parser = argparse.ArgumentParser(description="SQL Antipattern Scanner")
    parser.add_argument("sql_file", nargs='?', help="Path to the SQL file to scan")
    parser.add_argument("--query", help="SQL query to scan")
    parser.add_argument("--format", choices=["json", "csv", "html"], default="json", help="Output format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--run-tests", action="store_true", help="Run unit tests")
    args = parser.parse_args()

    if args.run_tests:
        print("Running unit tests...")
        run_tests()
        print("Unit tests completed.")

    if args.sql_file:
        print(f"Scanning SQL file: {args.sql_file}")
        with open(args.sql_file, 'r') as f:
            sql = f.read()
    elif args.query:
        print("Scanning SQL query")
        sql = args.query
    else:
        parser.error("Either sql_file or --query must be specified")

    scanner = SQLAntipatternScanner()
    issues = scanner.scan_sql(sql)
    report = scanner.generate_report(issues, sql, format=args.format)

    if args.output:
        mode = 'w' if args.format != 'csv' else 'w'
        with open(args.output, mode, newline='') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print("Scan report:")
        print(report)

if __name__ == "__main__":
    main()