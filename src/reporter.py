"""
Reporter module for the sprint simulator.

This module provides HTML report generation from simulation history,
creating interactive visualizations of sprint progress.
"""

import json

from src.feature import FeatureStage
from src.history import SprintHistory


class HTMLReporter:
    """
    Generates a standalone HTML report from simulation history.

    The report includes:
    - Interactive timeline slider
    - Feature progress table
    - Employee activity table
    - Code review tracking

    Example:
        >>> reporter = HTMLReporter(simulator.history)
        >>> reporter.save_report("sprint_report.html")
    """

    def __init__(self, history: SprintHistory) -> None:
        """
        Initialize the reporter.

        Args:
            history: SprintHistory instance with recorded simulation data.
        """
        self.history = history

    def save_report(self, filename: str = "sprint_report.html") -> None:
        """
        Generate and save the HTML report.

        Args:
            filename: Output file path for the HTML report.
        """
        print(f"🖨️ Generating HTML report: {filename}...")

        # Prepare data structures
        slider_data = self._prepare_slider_data()
        feature_table_html = self._generate_feature_table()
        employee_table_html = self._generate_employee_table()

        html_content = self._get_html_template(
            slider_data_json=json.dumps(slider_data),
            feature_table=feature_table_html,
            employee_table=employee_table_html,
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Report saved successfully!")

    def _prepare_slider_data(self) -> list[dict]:
        """
        Convert history into JSON-serializable structure for JS slider.

        Returns:
            List of tick data dictionaries for JavaScript consumption.
        """
        data = []

        for snap in self.history.history:
            tick_data: dict = {
                "tick_label": snap.tick.label,
                "features": [],
                "employees": [],
            }

            # Features processing
            for f in snap.features:
                remaining_sum = sum(f.remaining_efforts.values())
                total = f.total_capacity if f.total_capacity > 0 else 1.0
                progress = round(100 * (1 - remaining_sum / total), 1)

                status = "Done" if f.is_done else f.current_stage.display_name()

                tick_data["features"].append({
                    "name": f.name,
                    "stage": f.current_stage.display_name(),
                    "progress": progress,
                    "status": status,
                })

            # Employees processing
            for e in snap.employees:
                task = e.current_task if e.current_task else "Idle"
                tick_data["employees"].append({
                    "name": e.name,
                    "task": task,
                    "status": "Working" if e.has_worked else "Idle",
                })

            data.append(tick_data)

        return data

    def _generate_feature_table(self) -> str:
        """
        Generate HTML for the Feature x Time table.

        Returns:
            HTML string for the feature progress table.
        """
        if not self.history.history:
            return "<p>No data</p>"

        headers = ["Time"] + [f.name for f in self.history.history[0].features]
        rows = []

        for snap in self.history.history:
            cells = [f"<td>{snap.tick.label}</td>"]

            for f in snap.features:
                if f.is_done:
                    content = "✅ Done"
                else:
                    stage_name = f.current_stage.display_name()
                    remaining = sum(f.remaining_efforts.values())
                    content = f"{stage_name} ({remaining:.1f}h left)"

                cells.append(f"<td>{content}</td>")

            rows.append("<tr>" + "".join(cells) + "</tr>")

        return self._render_table_html("Feature Progress", headers, rows)

    def _generate_employee_table(self) -> str:
        """
        Generate HTML for the Employee x Time table.

        Returns:
            HTML string for the employee activity table.
        """
        if not self.history.history:
            return "<p>No data</p>"

        headers = ["Time"] + [e.name for e in self.history.history[0].employees]
        rows = []

        for snap in self.history.history:
            cells = [f"<td>{snap.tick.label}</td>"]

            for e in snap.employees:
                if e.has_worked:
                    content = f"🛠 {e.current_task}"
                    css_class = "status-working"
                else:
                    content = "😴 Idle"
                    css_class = "status-idle"

                cells.append(f'<td class="{css_class}">{content}</td>')

            rows.append("<tr>" + "".join(cells) + "</tr>")

        return self._render_table_html("Employee Activity", headers, rows)

    def _render_table_html(
        self,
        title: str,
        headers: list[str],
        rows: list[str],
    ) -> str:
        """
        Render a standard styled HTML table.

        Args:
            title: Table heading text.
            headers: Column header names.
            rows: HTML row strings.

        Returns:
            Complete HTML table string.
        """
        header_html = "".join([f"<th>{h}</th>" for h in headers])
        body_html = "\n".join(rows)

        return f"""
        <h3>{title}</h3>
        <div class="table-container">
            <table>
                <thead><tr>{header_html}</tr></thead>
                <tbody>{body_html}</tbody>
            </table>
        </div>
        """

    def _get_html_template(
        self,
        slider_data_json: str,
        feature_table: str,
        employee_table: str,
    ) -> str:
        """
        Generate the complete HTML document.

        Args:
            slider_data_json: JSON string of slider data.
            feature_table: HTML for feature table.
            employee_table: HTML for employee table.

        Returns:
            Complete HTML document string.
        """
        max_tick = len(self.history.history) - 1 if self.history.history else 0

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sprint Simulation Report</title>
    <style>
        :root {{
            --bg-color: #1e1e1e;
            --text-color: #e0e0e0;
            --card-bg: #252526;
            --border-color: #3e3e42;
            --accent-color: #4fc1ff;
            --success-color: #89d185;
            --warning-color: #dcdcaa;
            --idle-color: #6e6e6e;
            --review-color: #ce9178;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}

        h1, h2, h3 {{ color: var(--accent-color); }}

        /* Tabs */
        .tabs {{
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
        }}

        .tab-button {{
            background-color: transparent;
            border: none;
            color: var(--text-color);
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
            opacity: 0.7;
            border-bottom: 2px solid transparent;
        }}

        .tab-button:hover {{ opacity: 1; }}
        .tab-button.active {{
            opacity: 1;
            border-bottom: 2px solid var(--accent-color);
            color: var(--accent-color);
        }}

        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}

        /* Slider View */
        .slider-controls {{
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        input[type=range] {{
            width: 100%;
            accent-color: var(--accent-color);
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 900px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
        }}

        .entity-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .entity-list li {{
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
        }}
        .entity-list li:last-child {{ border-bottom: none; }}

        /* Progress Bar */
        .progress-container {{
            width: 100%;
            background-color: var(--border-color);
            border-radius: 4px;
            height: 8px;
            margin-top: 5px;
            overflow: hidden;
        }}
        .progress-bar {{
            height: 100%;
            background-color: var(--success-color);
            transition: width 0.1s linear;
        }}

        /* Stage badges */
        .stage-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .stage-analytics {{ background-color: #6a9955; }}
        .stage-development {{ background-color: #569cd6; }}
        .stage-code_review {{ background-color: #ce9178; }}
        .stage-testing {{ background-color: #c586c0; }}

        /* Tables */
        .table-container {{
            max-height: 70vh;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th, td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        thead {{
            background-color: #333;
            position: sticky;
            top: 0;
            z-index: 1;
        }}

        tbody tr:hover {{
            background-color: #2a2d2e;
        }}

        .status-working {{ color: var(--success-color); font-weight: bold; }}
        .status-idle {{ color: var(--idle-color); font-style: italic; }}
        .status-review {{ color: var(--review-color); }}
    </style>
</head>
<body>

    <h1>🚀 Sprint Simulation Report</h1>

    <!-- Tabs -->
    <div class="tabs">
        <button class="tab-button active" onclick="openTab(event, 'SliderTab')">📊 Timeline Slider</button>
        <button class="tab-button" onclick="openTab(event, 'FeatureTab')">📦 Features Table</button>
        <button class="tab-button" onclick="openTab(event, 'EmployeeTab')">👥 Employees Table</button>
    </div>

    <!-- Tab 1: Slider -->
    <div id="SliderTab" class="tab-content active">
        <div class="slider-controls">
            <span>Tick:</span>
            <input type="range" min="0" max="{max_tick}" value="0" id="timeSlider" oninput="updateView(this.value)">
            <span id="tickLabel" style="font-weight:bold; min-width: 150px;">Day 1 - Hour 1</span>
        </div>

        <div class="dashboard">
            <div class="card">
                <h3>📦 Features Status</h3>
                <ul id="featuresList" class="entity-list"></ul>
            </div>
            <div class="card">
                <h3>👥 Employees Status</h3>
                <ul id="employeesList" class="entity-list"></ul>
            </div>
        </div>
    </div>

    <!-- Tab 2: Feature Table -->
    <div id="FeatureTab" class="tab-content">
        {feature_table}
    </div>

    <!-- Tab 3: Employee Table -->
    <div id="EmployeeTab" class="tab-content">
        {employee_table}
    </div>

    <script>
        const historyData = {slider_data_json};

        function getStageClass(stage) {{
            const classes = {{
                'Analytics': 'stage-analytics',
                'Development': 'stage-development',
                'Code Review': 'stage-code_review',
                'Testing': 'stage-testing',
                'Done': 'stage-done'
            }};
            return classes[stage] || '';
        }}

        function updateView(index) {{
            const data = historyData[index];

            // Update Label
            document.getElementById('tickLabel').innerText = data.tick_label;

            // Update Features
            const fList = document.getElementById('featuresList');
            fList.innerHTML = '';
            data.features.forEach(f => {{
                const li = document.createElement('li');
                li.innerHTML = `
                    <div style="flex-grow: 1;">
                        <div style="display:flex; justify-content:space-between;">
                            <span><b>${{f.name}}</b></span>
                            <span>${{f.progress}}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${{f.progress}}%"></div>
                        </div>
                        <small>
                            <span class="stage-badge ${{getStageClass(f.stage)}}">${{f.stage}}</span>
                        </small>
                    </div>
                `;
                fList.appendChild(li);
            }});

            // Update Employees
            const eList = document.getElementById('employeesList');
            eList.innerHTML = '';
            data.employees.forEach(e => {{
                const li = document.createElement('li');
                let icon = '😴';
                let color = 'var(--idle-color)';
                let extraClass = '';

                if (e.status === 'Working') {{
                    icon = '🛠';
                    color = 'var(--success-color)';
                    // Check if doing code review
                    if (e.task && e.task.includes && !e.task.includes('Idle')) {{
                        extraClass = 'status-working';
                    }}
                }}

                li.innerHTML = `
                    <span>${{icon}} <b>${{e.name}}</b></span>
                    <span style="color: ${{color}}" class="${{extraClass}}">${{e.task}}</span>
                `;
                eList.appendChild(li);
            }});
        }}

        function openTab(evt, tabName) {{
            // Hide all tabs
            const tabcontent = document.getElementsByClassName("tab-content");
            for (let i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}

            // Remove active class
            const tablinks = document.getElementsByClassName("tab-button");
            for (let i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}

            // Show current tab
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}

        // Initial render
        updateView(0);
    </script>
</body>
</html>
        """
