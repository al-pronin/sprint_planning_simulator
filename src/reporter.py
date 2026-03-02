"""
Reporter module for the sprint simulator.

Generates HTML reports with interactive visualizations of the sprint,
including bug fix tracking and contributor analysis.
"""

import json
from typing import TYPE_CHECKING

from src.feature import FeatureStage
from src.history import SprintHistory

if TYPE_CHECKING:
    pass


class HTMLReporter:
    """
    Generates standalone HTML reports from simulation history.

    The report includes:
    - Interactive timeline slider
    - Feature progress table with bug tracking
    - Employee activity table
    - Bug fix visualization showing dev + QA pairs
    """

    # Stage display styles
    STAGE_COLORS: dict[str, str] = {
        "Analytics": "#6a9955",
        "Development": "#569cd6",
        "Code Review": "#ce9178",
        "Testing": "#c586c0",
        "Bug Fix": "#f14c4c",
        "Done": "#89d185",
    }

    def __init__(self, history: SprintHistory) -> None:
        """
        Initialize the reporter.

        Args:
            history: SprintHistory with recorded simulation data.
        """
        self.history = history

    def save_report(self, filename: str = "sprint_report.html") -> None:
        """Generate and save the HTML report."""
        print(f"🖨️ Generating HTML report: {filename}...")

        slider_data = self._prepare_slider_data()
        feature_table = self._generate_feature_table()
        employee_table = self._generate_employee_table()
        stats_panel = self._generate_stats_panel()

        html = self._build_html(
            slider_data_json=json.dumps(slider_data),
            feature_table=feature_table,
            employee_table=employee_table,
            stats_panel=stats_panel,
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ Report saved successfully!")

    def _prepare_slider_data(self) -> list[dict]:
        """Prepare JSON-serializable data for the JavaScript slider."""
        data = []

        for snap in self.history.history:
            tick_data: dict = {
                "tick_label": snap.tick.label,
                "features": [],
                "employees": [],
            }

            # Process features
            for f in snap.features:
                remaining = sum(f.remaining_efforts.values())
                total = f.total_capacity if f.total_capacity > 0 else 1.0
                progress = round(100 * (1 - remaining / total), 1)

                status = "Done" if f.is_done else f.current_stage.display_name()
                stage_color = self.STAGE_COLORS.get(status, "#6e6e6e")

                tick_data["features"].append({
                    "name": f.name,
                    "stage": f.current_stage.display_name(),
                    "progress": progress,
                    "status": status,
                    "stage_color": stage_color,
                    "has_bugs": f.has_bugs,
                    "dev_contributors": list(f.development_contributors),
                    "qa_contributors": list(f.testing_contributors),
                })

            # Process employees
            for e in snap.employees:
                tick_data["employees"].append({
                    "name": e.name,
                    "task": e.current_task or "Idle",
                    "status": "Working" if e.has_worked else "Idle",
                })

            data.append(tick_data)

        return data

    def _generate_feature_table(self) -> str:
        """Generate the Feature x Time table HTML."""
        if not self.history.history:
            return "<p>No simulation data</p>"

        first_snap = self.history.history[0]
        headers = ["Time"] + [f.name for f in first_snap.features]

        rows = []
        for snap in self.history.history:
            cells = [f"<td>{snap.tick.label}</td>"]

            for f in snap.features:
                if f.is_done:
                    content = "✅ Done"
                    css_class = "status-done"
                else:
                    stage = f.current_stage.display_name()
                    remaining = sum(f.remaining_efforts.values())

                    # Special formatting for bug fix
                    if f.current_stage == FeatureStage.BUG_FIX:
                        devs = ", ".join(f.development_contributors)
                        qas = ", ".join(f.testing_contributors)
                        content = (
                            f"🐛 Bug Fix ({remaining:.1f}h)<br>"
                            f"<small>Dev: {devs or '—'} | QA: {qas or '—'}</small>"
                        )
                        css_class = "status-bugfix"
                    else:
                        content = f"{stage} ({remaining:.1f}h left)"
                        css_class = f"status-{f.current_stage.value}"

                cells.append(f'<td class="{css_class}">{content}</td>')

            rows.append("<tr>" + "".join(cells) + "</tr>")

        return self._render_table("Feature Progress", headers, rows)

    def _generate_employee_table(self) -> str:
        """Generate the Employee x Time table HTML."""
        if not self.history.history:
            return "<p>No simulation data</p>"

        first_snap = self.history.history[0]
        headers = ["Time"] + [e.name for e in first_snap.employees]

        rows = []
        for snap in self.history.history:
            cells = [f"<td>{snap.tick.label}</td>"]

            for e in snap.employees:
                if e.has_worked:
                    # Parse task to check for bug fix
                    task = e.current_task or "Unknown"
                    if "Bug Fix" in task:
                        icon = "🐛"
                        css_class = "status-bugfix"
                    else:
                        icon = "🛠"
                        css_class = "status-working"

                    content = f"{icon} {task}"
                else:
                    content = "😴 Idle"
                    css_class = "status-idle"

                cells.append(f'<td class="{css_class}">{content}</td>')

            rows.append("<tr>" + "".join(cells) + "</tr>")

        return self._render_table("Employee Activity", headers, rows)

    def _generate_stats_panel(self) -> str:
        """Generate a statistics panel for the report."""
        if not self.history.history:
            return ""

        last_snap = self.history.history[-1]
        total_ticks = len(self.history.history)
        total_days = last_snap.tick.day

        # Count completed features
        done = sum(1 for f in last_snap.features if f.is_done)
        total = len(last_snap.features)

        # Count bugs
        with_bugs = sum(1 for f in last_snap.features if f.has_bugs is True)
        without_bugs = sum(1 for f in last_snap.features if f.has_bugs is False)

        return f"""
        <div class="stats-panel">
            <div class="stat-card">
                <div class="stat-value">{total_days}</div>
                <div class="stat-label">Working Days</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{done}/{total}</div>
                <div class="stat-label">Features Done</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{with_bugs}</div>
                <div class="stat-label">Features with Bugs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{without_bugs}</div>
                <div class="stat-label">Clean Features</div>
            </div>
        </div>
        """

    def _render_table(
        self,
        title: str,
        headers: list[str],
        rows: list[str],
    ) -> str:
        """Render a styled HTML table."""
        header_html = "".join(f"<th>{h}</th>" for h in headers)
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

    def _build_html(
        self,
        *,
        slider_data_json: str,
        feature_table: str,
        employee_table: str,
        stats_panel: str,
    ) -> str:
        """Build the complete HTML document."""
        max_tick = len(self.history.history) - 1 if self.history.history else 0

        return f"""<!DOCTYPE html>
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
            --idle-color: #6e6e6e;
            --bug-color: #f14c4c;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}

        h1 {{ color: var(--accent-color); }}
        h2, h3 {{ color: #dcdcaa; }}

        .stats-panel {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .stat-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px 25px;
            text-align: center;
            flex: 1;
            min-width: 120px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--accent-color);
        }}

        .stat-label {{
            font-size: 0.9em;
            color: var(--idle-color);
        }}

        .tabs {{
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            gap: 5px;
        }}

        .tab-button {{
            background-color: transparent;
            border: none;
            color: var(--text-color);
            padding: 10px 20px;
            cursor: pointer;
            font-size: 14px;
            opacity: 0.7;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }}

        .tab-button:hover {{ opacity: 1; }}
        .tab-button.active {{
            opacity: 1;
            border-bottom-color: var(--accent-color);
            color: var(--accent-color);
        }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

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
            .dashboard {{ grid-template-columns: 1fr; }}
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
        }}

        .entity-list li:last-child {{ border-bottom: none; }}

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

        tbody tr:hover {{ background-color: #2a2d2e; }}

        .status-working {{ color: var(--success-color); font-weight: bold; }}
        .status-idle {{ color: var(--idle-color); font-style: italic; }}
        .status-done {{ color: var(--success-color); font-weight: bold; }}
        .status-bugfix {{ color: var(--bug-color); font-weight: bold; }}
        .status-testing {{ color: #c586c0; }}
        .status-development {{ color: #569cd6; }}
        .status-code_review {{ color: #ce9178; }}
        .status-analytics {{ color: #6a9955; }}

        small {{ opacity: 0.7; font-size: 0.85em; }}
    </style>
</head>
<body>

    <h1>🚀 Sprint Simulation Report</h1>

    {stats_panel}

    <div class="tabs">
        <button class="tab-button active" onclick="openTab(event, 'SliderTab')">📊 Timeline</button>
        <button class="tab-button" onclick="openTab(event, 'FeatureTab')">📦 Features</button>
        <button class="tab-button" onclick="openTab(event, 'EmployeeTab')">👥 Employees</button>
    </div>

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

    <div id="FeatureTab" class="tab-content">{feature_table}</div>
    <div id="EmployeeTab" class="tab-content">{employee_table}</div>

    <script>
        const historyData = {slider_data_json};

        function updateView(index) {{
            const data = historyData[index];
            document.getElementById('tickLabel').innerText = data.tick_label;

            const fList = document.getElementById('featuresList');
            fList.innerHTML = '';
            data.features.forEach(f => {{
                const li = document.createElement('li');
                let bugIndicator = f.has_bugs ? ' 🐛' : '';
                li.innerHTML = `
                    <div>
                        <div style="display:flex; justify-content:space-between;">
                            <span><b>${{f.name}}</b>${{bugIndicator}}</span>
                            <span>${{f.progress}}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${{f.progress}}%; background-color: ${{f.stage_color}}"></div>
                        </div>
                        <small style="color: ${{f.stage_color}}">${{f.status}}</small>
                    </div>
                `;
                fList.appendChild(li);
            }});

            const eList = document.getElementById('employeesList');
            eList.innerHTML = '';
            data.employees.forEach(e => {{
                const li = document.createElement('li');
                const icon = e.status === 'Working' ? '🛠' : '😴';
                const color = e.status === 'Working' ? 'var(--success-color)' : 'var(--idle-color)';
                li.innerHTML = `
                    <span>${{icon}} <b>${{e.name}}</b></span>
                    <span style="color: ${{color}}">${{e.task}}</span>
                `;
                eList.appendChild(li);
            }});
        }}

        function openTab(evt, tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab-button').forEach(el => el.className = el.className.replace(' active', ''));
            document.getElementById(tabName).style.display = 'block';
            evt.currentTarget.className += ' active';
        }}

        updateView(0);
    </script>
</body>
</html>"""
