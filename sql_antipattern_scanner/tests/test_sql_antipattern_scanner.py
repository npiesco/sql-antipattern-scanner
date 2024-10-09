# sql-antipattern-scanner/test_sql_antipattern_scanner.py
from sql_antipattern_scanner.sql_antipattern_scanner import SQLAntipatternScanner

import unittest
from typing import List, Tuple, Any

class TestSQLAntipatternScanner(unittest.TestCase):
    """
    Test suite for SQLAntipatternScanner class.
    """

    def setUp(self) -> None:
        """
        Set up test environment before each test method.
        """
        self.scanner: SQLAntipatternScanner = SQLAntipatternScanner()

    def test_select_star(self) -> None:
        """
        Test detection of 'SELECT *' antipattern.
        """
        sql: str = "SELECT * FROM users"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[0][1], "SELECT *")

    def test_ansi89_join(self) -> None:
        """
        Test detection of 'ANSI-89 join' antipattern in various SQL statements.
        """
        sql_single_line: str = "SELECT u.name FROM users u, orders o WHERE u.id = o.user_id"
        sql_multi_line: str = """
        SELECT u.name 
        FROM users u, 
            orders o 
        WHERE u.id = o.user_id
        """
        sql_subquery_join: str = "SELECT * FROM (SELECT id FROM users) u, (SELECT id FROM orders) o"
        sql_complex: str = """
        SELECT u.name, o.order_date, (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id) as item_count
        FROM users u, orders o, (SELECT * FROM products WHERE in_stock = 1) p
        WHERE u.id = o.user_id AND o.product_id = p.id
        """
        
        issues_single: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_single_line)
        issues_multi: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_multi_line)
        issues_subquery_join: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_subquery_join)
        issues_complex: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_complex)
        
        self.assertEqual(len(issues_single), 1)
        self.assertEqual(issues_single[0][0].name, "ANSI-89 Join")
        self.assertIn("users u, orders o", issues_single[0][1])
        
        self.assertEqual(len(issues_multi), 1)
        self.assertEqual(issues_multi[0][0].name, "ANSI-89 Join")
        self.assertIn("users u, orders o", issues_multi[0][1])
        
        self.assertEqual(len(issues_subquery_join), 2)  # ANSI-89 Join and SELECT *
        self.assertTrue(any(issue[0].name == "ANSI-89 Join" for issue in issues_subquery_join))
        self.assertTrue(any(issue[0].name == "SELECT *" for issue in issues_subquery_join))
        
        self.assertEqual(len(issues_complex), 2)  # ANSI-89 Join and SELECT *
        self.assertTrue(any(issue[0].name == "ANSI-89 Join" for issue in issues_complex))
        self.assertTrue(any(issue[0].name == "SELECT *" for issue in issues_complex))
        ansi89_issue = next(issue for issue in issues_complex if issue[0].name == "ANSI-89 Join")
        self.assertIn("users u, orders o, (SELECT * FROM products WHERE in_stock = 1) p", ansi89_issue[1])

    def test_null_comparison(self) -> None:
        """
        Test detection of 'NULL' comparison antipattern.
        """
        sql_equal_null: str = "SELECT * FROM users WHERE status = NULL"
        sql_is_null: str = "SELECT * FROM users WHERE status IS NULL"
        sql_not_null: str = "SELECT * FROM users WHERE status IS NOT NULL"
        
        issues_equal_null: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_equal_null)
        issues_is_null: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_is_null)
        issues_not_null: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql_not_null)
        
        self.assertEqual(len(issues_equal_null), 2)  # SELECT * and NULL Comparison
        self.assertEqual(issues_equal_null[0][0].name, "SELECT *")
        self.assertEqual(issues_equal_null[1][0].name, "NULL Comparison")
        self.assertEqual(issues_equal_null[1][1], "status = NULL")
        
        self.assertEqual(len(issues_is_null), 1)  # Only SELECT *
        self.assertEqual(issues_is_null[0][0].name, "SELECT *")
        
        self.assertEqual(len(issues_not_null), 1)  # Only SELECT *
        self.assertEqual(issues_not_null[0][0].name, "SELECT *")

    def test_wildcard_detection(self) -> None:
        """
        Test detection of different wildcard usages in 'LIKE' clauses.
        """
        sql: str = """
        SELECT * FROM users
        WHERE name LIKE '%John'
        AND email LIKE 'user@%'
        AND description LIKE '%important%'
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        wildcard_issues: List[Tuple[Any, str, str]] = [issue for issue in issues if issue[0].name in ["Leading Wildcard", "Trailing Wildcard", "Both-sided Wildcard"]]
        self.assertEqual(len(wildcard_issues), 3)
        wildcard_names: List[str] = [issue[0].name for issue in wildcard_issues]
        self.assertIn("Leading Wildcard", wildcard_names)
        self.assertIn("Trailing Wildcard", wildcard_names)
        self.assertIn("Both-sided Wildcard", wildcard_names)

    def test_function_in_where(self) -> None:
        """
        Test detection of various functions used in 'WHERE' clause.
        """
        sql: str = """
        SELECT * FROM users 
        WHERE UPPER(name) = 'JOHN' 
        AND LOWER(email) LIKE '%@example.com' 
        AND CONCAT(first_name, ' ', last_name) = 'John Doe'
        AND DATE(created_at) = '2023-01-01'
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        function_issues: List[Tuple[Any, str, str]] = [issue for issue in issues if issue[0].name == "Function in WHERE"]
        self.assertEqual(len(function_issues), 4)

    def test_no_issues(self) -> None:
        """
        Test query with no antipatterns.
        """
        sql: str = "SELECT id, name FROM users WHERE id > 100"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 0)

    def test_between_operator(self) -> None:
        """
        Test detection of 'BETWEEN' operator.
        """
        sql: str = "SELECT * FROM products WHERE price BETWEEN 100 AND 500"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and BETWEEN Operator
        self.assertEqual(issues[1][0].name, "BETWEEN Operator")
        self.assertEqual(issues[1][1], "BETWEEN")

    def test_subquery_in_in_clause(self) -> None:
        """
        Test detection of subquery in 'IN' clause.
        """
        sql: str = """
        SELECT *
        FROM users
        WHERE id IN (
            SELECT user_id
            FROM orders
            WHERE total > 1000
        )
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        antipattern_names: List[str] = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Subquery in IN clause", antipattern_names)

    def test_numeric_group_by(self) -> None:
        """
        Test detection of numeric 'GROUP BY'.
        """
        sql: str = "SELECT id, name FROM users GROUP BY 1, 2"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0].name, "Numeric GROUP BY")
        self.assertIn("GROUP BY 1, 2", issues[0][1])

    def test_case_insensitive_matching(self) -> None:
        """
        Test case-insensitive matching of SQL keywords and identifiers.
        """
        sql: str = "select * from Users WHERE Name LIKE '%John%'"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        antipattern_names: List[str] = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Both-sided Wildcard", antipattern_names)

    def test_sql_with_comments(self) -> None:
        """
        Test SQL with comments.
        """
        sql: str = """
        -- This is a comment
        SELECT * -- Inline comment
        FROM users
        WHERE status = NULL -- Another comment
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and NULL Comparison
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "NULL Comparison")

    def test_ignored_patterns(self) -> None:
        """
        Test ignored patterns.
        """
        self.scanner.ignore_pattern("SELECT *")
        sql: str = "SELECT * FROM users WHERE id > 100"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 0)
        # Reset ignored patterns for other tests
        self.scanner.ignored_patterns.clear()

    def test_multiple_antipatterns(self) -> None:
        """
        Test detection of multiple antipatterns in single query.
        """
        sql: str = """
        SELECT * 
        FROM users u, orders o 
        WHERE u.id = o.user_id 
        AND u.name LIKE '%John%' 
        AND o.status = NULL
        ORDER BY RAND()
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        antipattern_names: List[str] = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("ANSI-89 Join", antipattern_names)
        self.assertIn("Both-sided Wildcard", antipattern_names)
        self.assertIn("NULL Comparison", antipattern_names)
        self.assertIn("ORDER BY RAND()", antipattern_names)

    def test_subquery_not_ansi89_join(self) -> None:
        """
        Test that subqueries are not mistaken for ANSI-89 joins.
        """
        sql: str = "SELECT * FROM (SELECT id FROM users) u WHERE u.id > 10"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertNotIn("ANSI-89 Join", [issue[0].name for issue in issues])

    def test_complex_nested_subqueries(self) -> None:
        """
        Test detection of complex nested subqueries.
        """
        sql: str = """
        SELECT *
        FROM users
        WHERE id IN (
            SELECT user_id
            FROM orders
            WHERE total > (
                SELECT AVG(total)
                FROM orders
                WHERE status = 'completed'
            )
        )
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        antipattern_names: List[str] = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Subquery in IN clause", antipattern_names)

    def test_distinct_usage(self) -> None:
        """
        Test detection of DISTINCT usage.
        """
        sql: str = "SELECT DISTINCT user_id FROM orders"
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertTrue(any(issue[0].name == "DISTINCT Usage" for issue in issues))

    def test_correlated_subquery(self) -> None:
        """
        Test detection of correlated subquery.
        """
        sql: str = """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.id
            AND oi.quantity > 10
        )
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertTrue(any(issue[0].name == "Correlated Subquery" for issue in issues))

    def test_complex_ansi89_join(self) -> None:
        """
        Test detection of complex ANSI-89 join involving multiple tables.
        """
        sql: str = """
        SELECT u.name, o.order_date, p.product_name
        FROM users u, orders o, order_items oi, products p
        WHERE u.id = o.user_id
        AND o.id = oi.order_id
        AND oi.product_id = p.id
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0].name, "ANSI-89 Join")
        self.assertIn("users u, orders o, order_items oi, products p", issues[0][1])
        self.assertIn("FROM users u, orders o, order_items oi, products p", issues[0][2])

    def test_mixed_join_syntax(self) -> None:
        """
        Test detection of mixed join syntax.
        """
        sql: str = """
        SELECT u.name, o.order_date, oi.quantity
        FROM users u
        JOIN orders o ON u.id = o.user_id, order_items oi
        WHERE o.id = oi.order_id
        """
        issues: List[Tuple[Any, str, str]] = self.scanner.scan_sql(sql)
        
        self.assertTrue(any(issue[0].name == "ANSI-89 Join" for issue in issues), "Failed to detect ANSI-89 Join in mixed syntax")
        ansi89_issue = next((issue for issue in issues if issue[0].name == "ANSI-89 Join"), None)
        if ansi89_issue:
            self.assertIn("order_items oi", ansi89_issue[1], "Failed to identify the correct table in ANSI-89 Join")

def run_tests() -> None:
    """
    Run all tests in TestSQLAntipatternScanner test suite.
    """
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLAntipatternScanner)
    unittest.TextTestRunner(verbosity=2).run(test_suite)