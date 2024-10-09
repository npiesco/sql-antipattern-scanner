# sql-antipattern-scanner/sql_antipattern_scanner/report_generator.py
import json
import csv
from io import StringIO
from jinja2 import Template

class ReportGenerator:
    def __init__(self):
        self.html_template = Template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SQL Antipattern Scan Report</title>
            <link rel="stylesheet" href="report_styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
        </head>
        <body>
            <header>
                <h1>SQL Antipattern Scan Report</h1>
            </header>
            <main>
                <section class="summary-container">
                    <div class="summary-card">
                        <div class="summary-item">
                            <h2>Total Issues</h2>
                            <div class="dropdown-box" onclick="toggleBreakdown('total-issues-breakdown')">
                                <p class="large-number">{{ total_issues }}</p>
                                <span class="dropdown-icon">&#9662;</span>
                            </div>
                            <div id="total-issues-breakdown" class="breakdown-content">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Severity</th>
                                            <th>Count</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                                        <tr>
                                            <td>{{ severity }}</td>
                                            <td>{{ severity_counts[severity] }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="summary-item">
                            <h2>Severity Score</h2>
                            <div class="dropdown-box" onclick="toggleBreakdown('severity-score-breakdown')">
                                <p class="large-number">{{ severity_score }}</p>
                                <span class="dropdown-icon">&#9662;</span>
                            </div>
                            <div id="severity-score-breakdown" class="breakdown-content">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Severity</th>
                                            <th>Calculation</th>
                                            <th>Score</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                                        <tr>
                                            <td>{{ severity }}</td>
                                            <td>{{ severity_counts[severity] }} x {{ severity_weights[severity] }}</td>
                                            <td>{{ severity_counts[severity] * severity_weights[severity] }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="instructions">
                        Click on the boxes to view the breakdown.
                    </div>
                    <div class="chart-card">
                        <h2>Severity Distribution</h2>
                        <div class="chart-container">
                            <canvas id="severityChart"></canvas>
                        </div>
                    </div>
                </section>

                <section class="detailed-findings">
                    <h2>Detailed Findings</h2>
                    <div id="issuesList">
                    {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                        {% for issue in issues if issue.severity == severity %}
                        <details class="issue" data-severity="{{ issue.severity.lower() }}">
                            <summary>
                                <span class="issue-name">{{ issue.name }}</span>
                                <span class="severity {{ issue.severity.lower() }}">{{ issue.severity }}</span>
                            </summary>
                            <div class="issue-details">
                                <p><strong>Description:</strong> {{ issue.description }}</p>
                                <p><strong>Suggestion:</strong> {{ issue.suggestion }}</p>
                                <div class="code-block">
                                    <h4>Offending SQL:</h4>
                                    <pre><code>{{ issue.offending_sql }}</code></pre>
                                </div>
                                <div class="code-block">
                                    <h4>Context:</h4>
                                    <pre><code>{{ issue.context }}</code></pre>
                                </div>
                                <div class="code-block">
                                    <h4>Remediation example:</h4>
                                    <pre><code>{{ issue.remediation }}</code></pre>
                                </div>
                            </div>
                        </details>
                        {% endfor %}
                    {% endfor %}
                    </div>
                </section>
                
                <section class="original-sql">
                    <h2>Original SQL</h2>
                    <pre><code>{{ original_sql }}</code></pre>
                </section>
                
                <!-- Add breakdown modals -->
                <div id="total-issues-breakdown" class="modal">
                    <div class="modal-content">
                        <span class="close" onclick="closeModal('total-issues-breakdown')">&times;</span>
                        <h2>Total Issues Breakdown</h2>
                        <ul>
                            {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                            <li>{{ severity }}: {{ severity_counts[severity] }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>

                <div id="severity-score-breakdown" class="modal">
                    <div class="modal-content">
                        <span class="close" onclick="closeModal('severity-score-breakdown')">&times;</span>
                        <h2>Severity Score Breakdown</h2>
                        <ul>
                            {% for severity in ['Critical', 'High', 'Medium', 'Low'] %}
                            <li>{{ severity }}: {{ severity_counts[severity] }} x {{ severity_weights[severity] }} = {{ severity_counts[severity] * severity_weights[severity] }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </main>
            <script>
                // Create severity distribution chart
                const severityCounts = {{ severity_counts | tojson }};
                const ctx = document.getElementById('severityChart').getContext('2d');
                
                // Calculate total and percentages
                const total = Object.values(severityCounts).reduce((a, b) => a + b, 0);
                const percentages = Object.fromEntries(
                    Object.entries(severityCounts).map(([key, value]) => [key, ((value / total) * 100).toFixed(1)])
                );

                const chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Critical', 'High', 'Low', 'Medium'],
                        datasets: [{
                            data: [severityCounts.Critical, severityCounts.High, severityCounts.Low, severityCounts.Medium],
                            backgroundColor: ['#FF0000', '#FFA500', '#008000', '#FFFF00']  // Red, Orange, Green, Yellow
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const percentage = percentages[label];
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            },
                            datalabels: {
                                formatter: (value, ctx) => {
                                    const label = ctx.chart.data.labels[ctx.dataIndex];
                                    return `${percentages[label]}%`;
                                },
                                color: 'white',
                                font: {
                                    weight: 'bold',
                                    size: 12
                                },
                                textStrokeColor: 'black',
                                textStrokeWidth: 4,
                                textShadowColor: 'black',
                                textShadowBlur: 3,
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });

                // Add click event listener to the chart
                {{ chart_click_listener }}

                function filterIssues(severity) {
                    const issues = document.querySelectorAll('.issue');
                    issues.forEach(issue => {
                        if (severity === 'all' || issue.dataset.severity === severity) {
                            issue.style.display = 'block';
                        } else {
                            issue.style.display = 'none';
                        }
                    });
                }
                
                function toggleBreakdown(breakdownId) {
                    const breakdown = document.getElementById(breakdownId);
                    breakdown.style.display = breakdown.style.display === 'none' ? 'block' : 'none';
                }
            </script>
        </body>
        </html>
        ''')

    def generate_json(self, report_data):
        return json.dumps(report_data, indent=2)

    def generate_csv(self, report_data):
        output = StringIO()
        csv_writer = csv.writer(output)
        
        # Write header
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

    def generate_html(self, report_data):
        # Calculate severity counts for the chart
        severity_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for issue in report_data['issues']:
            severity_counts[issue['severity']] += 1
        report_data['severity_counts'] = severity_counts
        
        # Add filter buttons
        filter_buttons = '''
        <div class="filter-buttons">
            <button onclick="filterIssues('all')">All</button>
            <button onclick="filterIssues('critical')">Critical</button>
            <button onclick="filterIssues('high')">High</button>
            <button onclick="filterIssues('medium')">Medium</button>
            <button onclick="filterIssues('low')">Low</button>
        </div>
        '''
        report_data['filter_buttons'] = filter_buttons
        
        # Add click event listener to the chart
        chart_click_listener = '''
        document.getElementById('severityChart').onclick = function(evt) {
            const activePoints = chart.getElementsAtEventForMode(evt, 'point', chart.options);
            if (activePoints.length > 0) {
                const clickedSeverity = chart.data.labels[activePoints[0].index].toLowerCase();
                filterIssues(clickedSeverity);
            }
        };
        '''
        report_data['chart_click_listener'] = chart_click_listener
        
        # Add severity weights
        severity_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        report_data['severity_weights'] = severity_weights
        
        return self.html_template.render(**report_data)