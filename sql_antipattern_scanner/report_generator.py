# sql-antipattern-scanner/report_generator.py
import json
import csv
from io import StringIO
from jinja2 import Template
import os
from typing import Dict, Any

class ReportGenerator:
    """
    Class for generating reports in various formats based on SQL antipattern scan results.
    """

    def __init__(self):
        """
        Initialize ReportGenerator with HTML template.
        """
        self.html_template: Template = Template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SQL Antipattern Scan Report</title>
            <style>
                {{ css_content }}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <header>
                <h1>SQL Antipattern Scan Report</h1>
            </header>
            <main>
                <h2>Summary</h2>
                <div class="summary-container">
                    <div class="summary-card">
                        <h3>Total Issues</h3>
                        <div class="summary-box" data-target="total-issues-breakdown">
                            <p class="large-number">{{ len(issues) }}</p>
                            <span class="toggle-icon">&#9662;</span>
                        </div>
                        <div id="total-issues-breakdown" class="breakdown" style="display: none;">
                            <h4>Issues Breakdown</h4>
                            <ul>
                                {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                                <li>{{ severity }}: {{ severity_counts[severity] }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        <h3>Severity Score</h3>
                        <div class="summary-box" data-target="severity-score-breakdown">
                            <p class="large-number">{{ severity_score }}</p>
                            <span class="toggle-icon">&#9662;</span>
                        </div>
                        <div id="severity-score-breakdown" class="breakdown" style="display: none;">
                            <h4>Score Calculation</h4>
                            <p>The severity score is calculated based on the number and severity of issues found.</p>
                            <ul>
                                <li>Critical: {{ severity_weights['Critical'] }} points</li>
                                <li>High: {{ severity_weights['High'] }} points</li>
                                <li>Medium: {{ severity_weights['Medium'] }} points</li>
                                <li>Low: {{ severity_weights['Low'] }} point</li>
                            </ul>
                        </div>
                    </div>
                    <div class="chart-card">
                        <h3>Severity Distribution</h3>
                        <div class="chart-container">
                            <canvas id="severityChart"></canvas>
                        </div>
                    </div>
                </div>
                <section class="detailed-findings">
                    <h2>Detailed Findings</h2>
                    {% for issue in issues %}
                    <details class="issue" data-severity="{{ issue['severity'].lower() }}">
                        <summary>
                            <span class="issue-name">{{ issue['name'] }}</span>
                            <span class="severity {{ issue['severity'].lower() }}">{{ issue['severity'] }}</span>
                        </summary>
                        <div class="issue-details">
                            <p><strong>Description:</strong> {{ issue['description'] }}</p>
                            <p><strong>Suggestion:</strong> {{ issue['suggestion'] }}</p>
                            <div class="code-block">
                                <h4>Offending SQL:</h4>
                                <pre><code>{{ issue['offending_sql'] }}</code></pre>
                            </div>
                            <div class="code-block">
                                <h4>Context:</h4>
                                <pre><code>{{ issue['context'] }}</code></pre>
                            </div>
                            <p><strong>Remediation:</strong> {{ issue['remediation'] }}</p>
                        </div>
                    </details>
                    {% endfor %}
                </section>
                <section class="original-sql">
                    <h2>Original SQL</h2>
                    <pre><code>{{ original_sql }}</code></pre>
                </section>
            </main>
            <script>
                {{ js_content }}
                const ctx = document.getElementById('severityChart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Critical', 'High', 'Medium', 'Low'],
                        datasets: [{
                            data: [{{ severity_counts['Critical'] }}, {{ severity_counts['High'] }}, {{ severity_counts['Medium'] }}, {{ severity_counts['Low'] }}],
                            backgroundColor: ['#FF0000', '#FFA500', '#FFFF00', '#008000']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            }
                        },
                        onClick: (event, elements) => {
                            if (elements.length > 0) {
                                const clickedSeverity = chart.data.labels[elements[0].index].toLowerCase();
                                filterIssues(clickedSeverity);
                            } else {
                                filterIssues('all');
                            }
                        }
                    }
                });

                // Dropdown toggle function
                document.addEventListener('DOMContentLoaded', function() {
                    const summaryBoxes = document.querySelectorAll('.summary-box');
                    summaryBoxes.forEach(box => {
                        box.addEventListener('click', function() {
                            const breakdownId = this.getAttribute('data-target');
                            const breakdown = document.getElementById(breakdownId);
                            breakdown.style.display = breakdown.style.display === 'none' ? 'block' : 'none';
                            this.classList.toggle('active');
                        });
                    });
                });

                // Filter issues function
                function filterIssues(severity) {
                    const issues = document.querySelectorAll('.issue');
                    issues.forEach(issue => {
                        if (severity === 'all' || issue.dataset.severity === severity) {
                            issue.style.display = 'block';
                        } else {
                            issue.style.display = 'none';
                        }
                    });

                    // Update active state of filter buttons if they exist
                    const buttons = document.querySelectorAll('.filter-buttons button');
                    buttons.forEach(button => {
                        button.classList.toggle('active', button.textContent.toLowerCase() === severity);
                    });
                }
            </script>
        </body>
        </html>
        ''')

    def generate_json(self, report_data: Dict[str, Any]) -> str:
        """
        Generate JSON report from given report data.

        :param report_data: Dictionary containing report data
        :return: JSON string representation of report
        """
        return json.dumps(report_data, indent=2)

    def generate_csv(self, report_data: Dict[str, Any]) -> str:
        """
        Generate CSV report from given report data.

        :param report_data: Dictionary containing report data
        :return: CSV string representation of report
        """
        output = StringIO()
        csv_writer = csv.writer(output)
        
        # Headers
        csv_writer.writerow(['Name', 'Severity', 'Description', 'Suggestion', 'Offending SQL', 'Context', 'Remediation'])
        
        # Write data
        for issue in report_data['issues']:
            csv_writer.writerow([
                issue['name'],
                issue['severity'],
                issue['description'],
                issue['suggestion'],
                issue['offending_sql'],
                issue['context'],
                issue['remediation']
            ])
        
        return output.getvalue()

    def generate_html(self, report_data: Dict[str, Any]) -> str:
        """
        Generate HTML report from given report data.

        :param report_data: Dictionary containing report data
        :return: HTML string representation of report
        """
        # Calculate severity counts for chart
        severity_counts: Dict[str, int] = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for issue in report_data['issues']:
            severity_counts[issue['severity']] += 1
        report_data['severity_counts'] = severity_counts
        
        # Severity weights
        severity_weights: Dict[str, int] = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        report_data['severity_weights'] = severity_weights
        
        # Calculate severity score
        severity_score: int = sum(severity_counts[severity] * severity_weights[severity] for severity in severity_counts)
        report_data['severity_score'] = severity_score

        # Read CSS file
        css_path: str = os.path.join(os.path.dirname(__file__), 'static', 'report_styles.css')
        with open(css_path, 'r') as css_file:
            css_content: str = css_file.read()

        # Add CSS content and len function to report data
        report_data['css_content'] = css_content
        report_data['len'] = len

        # JavaScript for interactivity
        js_content: str = '''
        function filterIssues(severity) {
            const issues = document.querySelectorAll('.issue');
            issues.forEach(issue => {
                if (severity === 'all' || issue.dataset.severity === severity) {
                    issue.style.display = 'block';
                } else {
                    issue.style.display = 'none';
                }
            });

            // Update active state of filter buttons if they exist
            const buttons = document.querySelectorAll('.filter-buttons button');
            buttons.forEach(button => {
                button.classList.toggle('active', button.textContent.toLowerCase() === severity);
            });
        }
        '''
        report_data['js_content'] = js_content

        # Sort issues by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        report_data['issues'] = sorted(report_data['issues'], key=lambda x: severity_order[x['severity']])

        # Render template with updated report data
        return self.html_template.render(**report_data)