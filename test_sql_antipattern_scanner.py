# sql-antipattern-scanner/test_sql_antipattern_scanner.py
from sql_antipattern_scanner import SQLAntipatternScanner

import unittest

class TestSQLAntipatternScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = SQLAntipatternScanner()

    def test_select_star(self):
        sql = "SELECT * FROM users"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[0][1], "SELECT *")

    def test_ansi89_join(self):
        sql_single_line = "SELECT u.name FROM users u, orders o WHERE u.id = o.user_id"
        sql_multi_line = """
        SELECT u.name 
        FROM users u, 
            orders o 
        WHERE u.id = o.user_id
        """
        issues_single = self.scanner.scan_sql(sql_single_line)
        issues_multi = self.scanner.scan_sql(sql_multi_line)
        
        self.assertEqual(len(issues_single), 1)
        self.assertEqual(issues_single[0][0].name, "ANSI-89 Join")
        self.assertIn("users u, orders o", issues_single[0][1])
        
        self.assertEqual(len(issues_multi), 1)
        self.assertEqual(issues_multi[0][0].name, "ANSI-89 Join")
        self.assertIn("users u,", issues_multi[0][1])
        self.assertIn("orders o", issues_multi[0][1])

    def test_null_comparison(self):
        sql = "SELECT * FROM users WHERE status = NULL"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and NULL Comparison
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "NULL Comparison")
        self.assertEqual(issues[1][1], "status = NULL")

    def test_leading_wildcard(self):
        sql = "SELECT * FROM users WHERE name LIKE '%John%'"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and Both-sided Wildcard
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "Both-sided Wildcard")
        self.assertEqual(issues[1][1], "LIKE '%John%'")

    def test_function_in_where(self):
        sql = "SELECT * FROM users WHERE LOWER(name) = 'john'"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and Function in WHERE
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "Function in WHERE")
        self.assertEqual(issues[1][1], "WHERE LOWER(name)")

    def test_no_issues(self):
        sql = "SELECT id, name FROM users WHERE id > 100"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 0)

    def test_between_operator(self):
        sql = "SELECT * FROM products WHERE price BETWEEN 100 AND 500"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and BETWEEN Operator
        self.assertEqual(issues[1][0].name, "BETWEEN Operator")
        self.assertEqual(issues[1][1], "BETWEEN")

    def test_subquery_in_in_clause(self):
        sql = """
        SELECT *
        FROM users
        WHERE id IN (
            SELECT user_id
            FROM orders
            WHERE total > 1000
        )
        """
        issues = self.scanner.scan_sql(sql)
        antipattern_names = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Subquery in IN clause", antipattern_names)

    def test_numeric_group_by(self):
        sql = "SELECT id, name FROM users GROUP BY 1, 2"
        issues = self.scanner.scan_sql(sql)
        print(f"Issues: {issues}")  # Debug print statement
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0].name, "Numeric GROUP BY")
        self.assertIn("GROUP BY 1, 2", issues[0][1])

    def test_case_insensitive_matching(self):
        sql = "select * from Users WHERE Name LIKE '%John%'"
        issues = self.scanner.scan_sql(sql)
        antipattern_names = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Both-sided Wildcard", antipattern_names)

    def test_sql_with_comments(self):
        sql = """
        -- This is a comment
        SELECT * -- Inline comment
        FROM users
        WHERE status = NULL -- Another comment
        """
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and NULL Comparison
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "NULL Comparison")

    def test_ignored_patterns(self):
        self.scanner.ignore_pattern("SELECT *")
        sql = "SELECT * FROM users WHERE id > 100"
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 0)
        # Reset ignored patterns for other tests
        self.scanner.ignored_patterns.clear()

    def test_multiple_antipatterns(self):
        sql = """
        SELECT * 
        FROM users u, orders o 
        WHERE u.id = o.user_id 
        AND u.name LIKE '%John%' 
        AND o.status = NULL
        ORDER BY RAND()
        """
        issues = self.scanner.scan_sql(sql)
        antipattern_names = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("ANSI-89 Join", antipattern_names)
        self.assertIn("Both-sided Wildcard", antipattern_names)
        self.assertIn("NULL Comparison", antipattern_names)
        self.assertIn("ORDER BY RAND()", antipattern_names)

    def test_subquery_not_ansi89_join(self):
        sql = "SELECT * FROM (SELECT id FROM users) u WHERE u.id > 10"
        issues = self.scanner.scan_sql(sql)
        self.assertNotIn("ANSI-89 Join", [issue[0].name for issue in issues])

    def test_sql_with_comments(self):
        sql = """
        -- This is a comment
        SELECT * -- Inline comment
        FROM users
        WHERE status = NULL -- Another comment
        """
        issues = self.scanner.scan_sql(sql)
        self.assertEqual(len(issues), 2)  # SELECT * and NULL Comparison
        self.assertEqual(issues[0][0].name, "SELECT *")
        self.assertEqual(issues[1][0].name, "NULL Comparison")

    def test_complex_nested_subqueries(self):
        sql = """
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
        issues = self.scanner.scan_sql(sql)
        antipattern_names = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Subquery in IN clause", antipattern_names)

    def test_case_insensitive_matching(self):
        sql = "select * from Users WHERE Name LIKE '%John%'"
        issues = self.scanner.scan_sql(sql)
        antipattern_names = [issue[0].name for issue in issues]
        self.assertIn("SELECT *", antipattern_names)
        self.assertIn("Both-sided Wildcard", antipattern_names)

    def test_enhanced_function_in_where(self):
        sql = """
        SELECT * FROM users 
        WHERE UPPER(name) = 'JOHN' 
        AND LOWER(email) LIKE '%@example.com' 
        AND CONCAT(first_name, ' ', last_name) = 'John Doe'
        AND DATE(created_at) = '2023-01-01'
        """
        issues = self.scanner.scan_sql(sql)
        function_issues = [issue for issue in issues if issue[0].name == "Function in WHERE"]
        self.assertEqual(len(function_issues), 4)

    def test_wildcard_detection(self):
        sql = """
        SELECT * FROM users
        WHERE name LIKE '%John'
        AND email LIKE 'user@%'
        AND description LIKE '%important%'
        """
        issues = self.scanner.scan_sql(sql)
        wildcard_issues = [issue for issue in issues if issue[0].name in ["Leading Wildcard", "Trailing Wildcard", "Both-sided Wildcard"]]
        self.assertEqual(len(wildcard_issues), 3)
        wildcard_names = [issue[0].name for issue in wildcard_issues]
        self.assertIn("Leading Wildcard", wildcard_names)
        self.assertIn("Trailing Wildcard", wildcard_names)
        self.assertIn("Both-sided Wildcard", wildcard_names)

    def test_distinct_usage(self):
        sql = "SELECT DISTINCT user_id FROM orders"
        issues = self.scanner.scan_sql(sql)
        self.assertTrue(any(issue[0].name == "DISTINCT Usage" for issue in issues))

    def test_correlated_subquery(self):
        sql = """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.id
            AND oi.quantity > 10
        )
        """
        issues = self.scanner.scan_sql(sql)
        self.assertTrue(any(issue[0].name == "Correlated Subquery" for issue in issues))


def run_tests():
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLAntipatternScanner)
    unittest.TextTestRunner(verbosity=2).run(test_suite)