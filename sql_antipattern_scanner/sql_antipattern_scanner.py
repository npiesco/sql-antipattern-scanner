# sql-antipattern-scanner/sql_antipattern_scanner.py
import re
import sqlparse 
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Function
from collections import namedtuple
from .antipatterns import DEFAULT_ANTIPATTERNS
from .report_generator import ReportGenerator
import json
from functools import lru_cache

Antipattern = namedtuple('Antipattern', ['name', 'description', 'severity', 'suggestion', 'remediation'])

class SQLAntipatternScanner:
    def __init__(self):
        self.patterns = DEFAULT_ANTIPATTERNS
        self.ignored_patterns = set()
        self.load_custom_antipatterns()

    def load_custom_antipatterns(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                custom_patterns = config.get('custom_antipatterns', [])
                for pattern in custom_patterns:
                    self.add_pattern(
                        re.compile(pattern['regex'], re.IGNORECASE),
                        Antipattern(**pattern['antipattern'])
                    )
        except FileNotFoundError:
            pass

    def add_pattern(self, pattern, antipattern):
        self.patterns.append((pattern, antipattern))

    def ignore_pattern(self, pattern_name):
        self.ignored_patterns.add(pattern_name)

    @lru_cache(maxsize=100)
    def scan_sql(self, sql):
        antipatterns = []
        parsed = sqlparse.parse(sql)[0]
        
        checks = [
            ("SELECT *", self.check_select_star),
            ("Subquery in IN clause", self.check_subquery_in_in_clause),
            ("ANSI-89 Join", self.check_ansi89_join),
            ("Function in WHERE", self.check_functions_in_where),
            ("Numeric GROUP BY", self.check_numeric_group_by),
        ]
        
        detected_antipatterns = set()
        for name, check_function in checks:
            if name not in self.ignored_patterns:
                for antipattern, offending_sql, context in check_function(parsed):
                    if antipattern.name not in detected_antipatterns:
                        antipatterns.append((antipattern, offending_sql, context))
                        detected_antipatterns.add(antipattern.name)
        
        
        # Apply regex checks for remaining antipatterns
        for pattern, antipattern in self.patterns:
            if antipattern.name not in self.ignored_patterns and antipattern.name not in detected_antipatterns:
                matches = pattern.finditer(str(parsed))
                for match in matches:
                    offending_sql = match.group(0)
                    context = self.get_context(str(parsed), match.start())
                    antipatterns.append((antipattern, offending_sql, context))
                    detected_antipatterns.add(antipattern.name)
        
        return antipatterns

    def apply_regex_checks(self, sql):
        antipatterns = []
        formatted_sql = sqlparse.format(sql, strip_comments=True, keyword_case='upper')
        formatted_sql_oneline = re.sub(r'\s+', ' ', formatted_sql)
        
        for pattern, antipattern in self.patterns:
            if antipattern.name not in self.ignored_patterns:
                if antipattern.name == "ANSI-89 Join":
                    matches = pattern.finditer(formatted_sql_oneline)
                    for match in matches:
                        if not re.search(r'\bGROUP\s+BY\b', match.group(0), re.IGNORECASE):
                            offending_sql = match.group(0)
                            context = self.get_context(formatted_sql, match.start())
                            antipatterns.append((antipattern, offending_sql, context))
                else:
                    matches = pattern.finditer(formatted_sql)
                    for match in matches:
                        offending_sql = match.group(0)
                        context = self.get_context(formatted_sql, match.start())
                        antipatterns.append((antipattern, offending_sql, context))
        
        return antipatterns

    def check_select_star(self, parsed):
        antipatterns = []
        select_seen = False
        for token in parsed.tokens:
            if token.ttype is sqlparse.tokens.DML and token.value.upper() == 'SELECT':
                select_seen = True
            elif select_seen and token.ttype is sqlparse.tokens.Wildcard:
                antipattern = next((ap for _, ap in self.patterns if ap.name == "SELECT *"), None)
                if antipattern:
                    antipatterns.append((antipattern, f"SELECT {str(token)}", self.get_context(str(parsed), parsed.token_index(token))))
                break
        return antipatterns

    def check_ansi89_join(self, parsed):
        antipatterns = []
        from_seen = False
        comma_join = False
        for token in parsed.tokens:
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                from_seen = True
            elif from_seen and isinstance(token, IdentifierList):
                if ',' in token.value and not any(subtoken.ttype is sqlparse.tokens.Keyword and subtoken.value.upper() in ['SELECT', 'GROUP BY'] for subtoken in token.tokens):
                    comma_join = True
                    break
            elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ['WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT']:
                break
        if comma_join:
            antipattern = next((ap for _, ap in self.patterns if ap.name == "ANSI-89 Join"), None)
            if antipattern:
                antipatterns.append((antipattern, str(token), self.get_context(str(parsed), parsed.token_index(token))))
        return antipatterns

    def check_numeric_group_by(self, parsed):
        antipatterns = []
        for token in parsed.tokens:
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'GROUP BY':
                group_by_clause = ""
                for next_token in parsed.tokens[parsed.token_index(token)+1:]:
                    if next_token.ttype is not sqlparse.tokens.Whitespace:
                        group_by_clause += str(next_token)
                        if next_token.ttype is sqlparse.tokens.Punctuation and next_token.value == ';':
                            break
                if re.search(r'\b\d+\b', group_by_clause):
                    antipattern = next((ap for _, ap in self.patterns if ap.name == "Numeric GROUP BY"), None)
                    if antipattern:
                        antipatterns.append((antipattern, f"GROUP BY {group_by_clause}", self.get_context(str(parsed), parsed.token_index(token))))
                    break
        return antipatterns

    def check_functions_in_where(self, parsed):
        antipatterns = []
        for token in parsed.tokens:
            if isinstance(token, Where):
                for sub_token in token.flatten():
                    if isinstance(sub_token, Function):
                        antipattern = next((ap for _, ap in self.patterns if ap.name == "Function in WHERE"), None)
                        if antipattern:
                            context_start = max(0, token.token_index(sub_token) - 50)
                            context_end = min(len(str(parsed)), token.token_index(sub_token) + len(str(sub_token)) + 50)
                            context = str(parsed)[context_start:context_end]
                            antipatterns.append((antipattern, str(sub_token), context))
        return antipatterns

    def check_subquery_in_in_clause(self, parsed):
        antipatterns = []
        def recursive_check(token):
            if isinstance(token, sqlparse.sql.TokenList):
                in_clause = False
                for t in token.tokens:
                    if t.ttype is sqlparse.tokens.Keyword and t.value.upper() == 'IN':
                        in_clause = True
                    elif in_clause and isinstance(t, sqlparse.sql.Parenthesis):
                        if any('SELECT' in str(st).upper() for st in t.flatten()):
                            antipattern = next((ap for _, ap in self.patterns if ap.name == "Subquery in IN clause"), None)
                            if antipattern:
                                antipatterns.append((antipattern, str(token), self.get_context(str(parsed), parsed.token_index(token))))
                        in_clause = False
                    recursive_check(t)
        
        recursive_check(parsed)
        return antipatterns

    def get_context(self, sql, position, context_chars=100):
        start = max(0, position - context_chars)
        end = min(len(sql), position + context_chars)
        return sql[start:end]

    def get_severity_score(self, antipatterns):
        severity_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        return sum(severity_map[ap.severity] for ap, _, _ in antipatterns)

    def generate_report(self, antipatterns, sql, format='json'):
        report_data = {
            "total_issues": len(antipatterns),
            "severity_score": self.get_severity_score(antipatterns),
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
                for ap, offending_sql, context in antipatterns
            ],
            "original_sql": sqlparse.format(sql, reindent=True, keyword_case='upper')
        }

        report_generator = ReportGenerator()
        if format == 'json':
            return report_generator.generate_json(report_data)
        elif format == 'csv':
            return report_generator.generate_csv(report_data)
        elif format == 'html':
            return report_generator.generate_html(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")