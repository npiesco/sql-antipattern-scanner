# sql_antipattern_scanner/sql_antipattern_scanner/antipatterns.py
import re
from collections import namedtuple

Antipattern = namedtuple('Antipattern', ['name', 'description', 'severity', 'suggestion', 'remediation'])

DEFAULT_ANTIPATTERNS = [
            (re.compile(r'\bSELECT\s+\*', re.IGNORECASE),
             Antipattern("SELECT *", "Using SELECT * instead of specifying columns can lead to performance issues and make queries brittle to schema changes.",
                         "Medium", "Explicitly list the columns you need in the SELECT statement.",
                         "SELECT column1, column2, column3 FROM table")),
            
            (re.compile(r'\bFROM\s+\w+(?:\s+\w+)?(?:\s*,\s*\w+(?:\s+\w+)?)+(?!\s*(?:WHERE|GROUP\s+BY|ORDER\s+BY|LIMIT|$))', re.IGNORECASE),
            Antipattern("ANSI-89 Join", "Using outdated ANSI-89 join syntax instead of explicit JOIN clauses can lead to logical errors and reduced readability.",
                        "Critical", "Use explicit JOIN clauses instead of comma-separated table lists.",
                        "FROM table1 INNER JOIN table2 ON table1.id = table2.id")),
            
            (re.compile(r'\b(\w+)\s*(=|!=)\s*NULL\b', re.IGNORECASE),
             Antipattern("NULL Comparison", "Incorrectly filtering for NULL using = or != instead of IS NULL or IS NOT NULL.",
                         "Critical", "Use IS NULL or IS NOT NULL for NULL comparisons.",
                         "WHERE column IS NULL")),
            
            (re.compile(r'\b(?:WHERE|AND)\s+(?:.*?(?:UPPER|LOWER|CONCAT|DATE|SUBSTRING|TRIM)\s*\([^)]*\).*?)+', re.IGNORECASE),
             Antipattern("Function in WHERE", "Using functions on columns in WHERE clauses can prevent index usage and slow down queries.",
                        "Medium", "Try to avoid using functions on columns in WHERE clauses.",
                        "WHERE column = 'value' instead of WHERE LOWER(column) = 'value'")),
            
            (re.compile(r'\bGROUP\s+BY\s+\d+', re.IGNORECASE),
             Antipattern("Numeric GROUP BY", "Using numbers in GROUP BY clauses instead of column names reduces readability and is prone to errors.",
                         "Low", "Use column names instead of numbers in GROUP BY clauses.",
                         "GROUP BY column1, column2 instead of GROUP BY 1, 2")),
            
            (re.compile(r'\bORDER\s+BY\s+RAND\(\)', re.IGNORECASE),
             Antipattern("ORDER BY RAND()", "Using ORDER BY RAND() for random sorting is inefficient for large datasets.",
                         "High", "Consider alternative methods for random selection, such as using a subquery with LIMIT.",
                         "SELECT * FROM (SELECT * FROM table ORDER BY RAND() LIMIT 10) t ORDER BY id")),
            
            (re.compile(r'\bIN\s*\(\s*SELECT', re.IGNORECASE),
             Antipattern("Subquery in IN clause", "Using a subquery in an IN clause can be inefficient. Consider using EXISTS or JOIN instead.",
                         "Medium", "Replace IN (SELECT ...) with EXISTS or JOIN for better performance.",
                         "WHERE EXISTS (SELECT 1 FROM subquery_table WHERE subquery_table.id = main_table.id)")),
            
            (re.compile(r'\bBETWEEN\b', re.IGNORECASE),
             Antipattern("BETWEEN Operator", "Using the BETWEEN operator can result in poor performance for large ranges or complex queries.",
                         "Medium", "Consider using explicit range conditions (e.g., col >= val1 AND col <= val2) for better index utilization.",
                         "WHERE column >= value1 AND column <= value2")),
            
            (re.compile(r'\bLIKE\s+[\'"]%.*?%[\'"]', re.IGNORECASE),
             Antipattern("Both-sided Wildcard", "Using wildcards on both sides in LIKE conditions can lead to poor performance and ineffective index usage.",
                         "High", "Avoid using both leading and trailing wildcards in LIKE conditions. Consider full-text search for complex pattern matching.",
                         "Use a full-text search index or LIKE 'value%' if possible")),

            (re.compile(r'\bLIKE\s+[\'"]%(?!.*%[\'"])', re.IGNORECASE),
             Antipattern("Leading Wildcard", "Using leading wildcards in LIKE clauses can lead to poor index utilization and slow queries.",
                         "Medium", "Avoid using leading wildcards in LIKE clauses if possible.",
                         "Use a full-text search index or reverse the column and search term")),

            (re.compile(r'\bLIKE\s+[\'"](?!%).+%[\'"]', re.IGNORECASE),
             Antipattern("Trailing Wildcard", "Using trailing wildcards in LIKE conditions can lead to poor performance for large datasets.",
                         "Low", "Consider using a full-text search solution for better performance with wildcard searches.",
                         "Use a full-text search index or LIKE 'value%' if possible")),
            
            (re.compile(r'\bDISTINCT\b', re.IGNORECASE),
             Antipattern("DISTINCT Usage", "Overuse of DISTINCT can lead to performance issues, especially with large datasets.",
                         "Medium", "Consider if DISTINCT is really necessary. Can the same result be achieved with proper JOINs or GROUP BY?",
                         "Use GROUP BY instead of DISTINCT when possible")),
            
            (re.compile(r'\bEXISTS\s*\(\s*SELECT', re.IGNORECASE),
             Antipattern("Correlated Subquery", "Correlated subqueries can lead to poor performance, especially with large datasets.",
                         "High", "Consider rewriting the query using JOINs or uncorrelated subqueries for better performance.",
                         "Use JOIN instead of EXISTS when possible"))
        ]