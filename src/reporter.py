import json
from typing import List
from src.history import SprintHistory, TickSnapshot, FeatureSnapshot, EmployeeSnapshot
from src.feature import FeatureStage


class HTMLReporter:
    """
    Generates a standalone HTML report from simulation history. 📝
    """

    def __init__(self, history: SprintHistory) -> None:
        self.history = history

    def save_report(self, filename: str = "sprint_report.html") -> None:
        """
        Generates and saves the HTML file.
        """
        print(f"🖨️ Generating HTML report: {filename}...")

        # Prepare data structures
        slider_data = self._prepare_slider_data()
        feature_table_html = self._generate_feature_table()
        employee_table_html = self._generate_employee_table()

        html_content = self._get_html_template(
            slider_data_json=json.dumps(slider_data),
            feature_table=feature_table_html,
            employee_table=employee_table_html
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Report saved successfully!")

    def _prepare_slider_data(self) -> List[dict]:
        """
        Converts history into a JSON-serializable structure for the JS slider.
        """
        data = []
        for snap in self.history.history:
            tick_data = {
                "tick_label": snap.tick.label,
                "features": [],
                "employees": []
            }

            # Features processing
            for f in snap.features:
                remaining_sum = sum(f.remaining_efforts.values())
                total = f.total_capacity if f.total_capacity > 0 else 1.0
                progress = round(100 * (1 - remaining_sum / total), 1)

                # Determine status text
                status = "Done" if f.is_done else f.current_stage.name.capitalize()

                tick_data["features"].append({
                    "name": f.name,
                    "stage": f.current_stage.name.capitalize(),
                    "progress": progress,
                    "status": status
                })

            # Employees processing
            for e in snap.employees:
                task = e.current_task if e.current_task else "Idle"
                tick_data["employees"].append({
                    "name": e.name,
                    "task": task,
                    "status": "Working" if e.has_worked else "Idle"
                })

            data.append(tick_data)
        return data

    def _generate_feature_table(self) -> str:
        """
        Generates HTML for the Feature x Time table.
        """
        if not self.history.history:
            return "<p>No data</p>"

        # Headers
        headers = ["Time"] + [f.name for f in self.history.history[0].features]

        rows = []
        for snap in self.history.history:
            cells = [f"<td>{snap.tick.label}</td>"]
            for f in snap.features:
                # If done, keep showing "Done"
                if f.is_done:
                    content = "✅ Done"
                else:
                    content = f"{f.current_stage.name.capitalize()} ({sum(f.remaining_efforts.values()):.1f}h left)"

                cells.append(f"<td>{content}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")

        return self._render_table_html("Feature Progress", headers, rows)

    def _generate_employee_table(self) -> str:
        """
        Generates HTML for the Employee x Time table.
        """
        if not self.history.history:
            return "<p>No data</p>"

        # Headers
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

    def _render_table_html(self, title: str, headers: List[str], rows: List[str]) -> str:
        """
        Helper to render a standard styled table.
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

    def _get_html_template(self, slider_data_json: str, feature_table: str, employee_table: str) -> str:
        """
        Returns the full HTML string with embedded CSS & JS.
        """
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
            --idle-color: #6e6e6e;
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

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
        }}

        .entity-list {{
            list-style: none;
            padding: 0;
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
            <input type="range" min="0" max="{len(self.history.history) - 1}" value="0" id="timeSlider" oninput="updateView(this.value)">
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
                        <small>${{f.status}}</small>
                    </div>
                `;
                fList.appendChild(li);
            }});

            // Update Employees
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