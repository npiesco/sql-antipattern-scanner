# sql_antipattern_scanner/sql_antipattern_scanner/cli.py
import argparse
from typing import List, Tuple, Any, Optional
from sql_antipattern_scanner import SQLAntipatternScanner
from sql_antipattern_scanner.tests.test_sql_antipattern_scanner import run_tests
from .report_generator import ReportGenerator
import sqlparse

def main() -> None:
    """
    Main function to run SQL Antipattern Scanner CLI.
    
    Parses command-line arguments, runs scanner on provided SQL,
    and generates report in specified format.
    """
    parser = argparse.ArgumentParser(description="SQL Antipattern Scanner")
    parser.add_argument("sql_file", nargs='?', help="Path to SQL file to scan")
    parser.add_argument("--query", help="SQL query to scan")
    parser.add_argument("--format", nargs='?', choices=["json", "csv", "html"], default="json", const="json", help="Output format (default: json)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--run-tests", action="store_true", help="Run unit tests")
    args = parser.parse_args()

    if args.run_tests:
        print("Running unit tests...")
        run_tests()
        print("Unit tests completed.")

    # Check if we need to generate a report
    if args.sql_file or args.query:
        sql: str = get_sql_input(args)

        scanner = SQLAntipatternScanner()
        issues: List[Tuple[Any, str, str]] = scanner.scan_sql(sql)
        
        report_data: dict = generate_report_data(scanner, issues, sql)

        report_generator = ReportGenerator()
        report: str = generate_report(report_generator, report_data, args.format)

        output_report(report, args.output, args.format)
    elif not args.run_tests:
        parser.print_help()

def get_sql_input(args: argparse.Namespace) -> str:
    """
    Get SQL input from file or command-line argument.

    :param args: Parsed command-line arguments
    :return: SQL query as a string
    :raises argparse.ArgumentTypeError: If neither sql_file nor query is provided
    """
    if args.sql_file:
        print(f"Scanning SQL file: {args.sql_file}")
        with open(args.sql_file, 'r') as f:
            return f.read()
    elif args.query:
        print("Scanning SQL query")
        return args.query
    else:
        raise argparse.ArgumentTypeError("Either sql_file or --query must be specified")

def generate_report_data(scanner: SQLAntipatternScanner, issues: List[Tuple[Any, str, str]], sql: str) -> dict:
    """
    Generate report data from scanner results.

    :param scanner: SQLAntipatternScanner instance
    :param issues: List of detected issues
    :param sql: Original SQL query
    :return: Dictionary containing report data
    """
    return {
        "total_issues": len(issues),
        "severity_score": scanner.get_severity_score(issues),
        "issues": [
            {
                "name": ap.name,
                "severity": ap.severity,
                "description": ap.description,
                "suggestion": ap.suggestion,
                "offending_sql": offending_sql,
                "context": context,
                "remediation": ap.remediation
            }
            for ap, offending_sql, context in issues
        ],
        "original_sql": sqlparse.format(sql, reindent=True, keyword_case='upper')
    }

def generate_report(report_generator: ReportGenerator, report_data: dict, format: str) -> str:
    """
    Generate report in specified format.

    :param report_generator: ReportGenerator instance
    :param report_data: Dictionary containing report data
    :param format: Desired output format ('json', 'csv', or 'html')
    :return: Generated report as string
    :raises ValueError: If an unsupported format is specified
    """
    if format == 'json':
        return report_generator.generate_json(report_data)
    elif format == 'csv':
        return report_generator.generate_csv(report_data)
    elif format == 'html':
        return report_generator.generate_html(report_data)
    else:
        raise ValueError(f"Unsupported format: {format}")

def output_report(report: str, output_file: Optional[str], format: str) -> None:
    """
    Output generated report to file or console.

    :param report: Generated report as string
    :param output_file: Path to output file (if specified)
    :param format: Report format ('json', 'csv', or 'html')
    """
    if output_file:
        mode = 'w' if format != 'csv' else 'w'
        with open(output_file, mode, newline='') as f:
            f.write(report)
        print(f"Report written to {output_file}")
    else:
        print("Scan report:")
        print(report)

if __name__ == "__main__":
    main()