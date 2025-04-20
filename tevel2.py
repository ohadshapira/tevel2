import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient
import json
import time



def get_all_documents():
    # Connect to local MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    documents=[]
    try:
        # Access database and collection
        db = client["tevel-15"]
        collection = db["telemetry"]  # Replace with your actual collection name

        # Fetch all documents
        documents = list(collection.find())

        # Convert ObjectId to string for JSON compatibility
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        client.close()

    except Exception as e:
        print(e)
        with open("tevel-15.json", "r", encoding="utf-8") as f:
            documents = json.load(f)

    finally:
        # Ensure the connection is closed
        client.close()
        return documents

def generate_html(data):
    param_data = defaultdict(list)
    ground_times = []
    dedications = []

    for entry in data:
        ground_time = pd.to_datetime(entry["groundTime"])
        ground_times.append(ground_time)

        params = {p["name"]: p["value"] for p in entry["params"]}
        for key in params:
            val = params[key]
            if isinstance(val, dict) and "$date" in val:
                val = pd.to_datetime(val["$date"])
            param_data[key].append(val)

        dedications.append(params.get("In memory of", None))

    expected_len = len(ground_times)
    for key in param_data:
        while len(param_data[key]) < expected_len:
            param_data[key].append(None)

    df_clean = pd.DataFrame(param_data)
    df_clean["groundTime"] = pd.to_datetime(ground_times)
    df_clean["In memory of"] = dedications
    df_clean.sort_values("groundTime", inplace=True)

    other_sections = []
    html_sections = []

    # === Plot each numeric parameter ===
    numeric_params = [
        col for col in df_clean.columns
        if col not in ["groundTime", "In memory of"] and pd.api.types.is_numeric_dtype(df_clean[col])
    ]

    # === Plot each remaining numeric parameter ===
    temp_params = [param for param in numeric_params if "solar" in param.lower() and "temp" in param.lower()]
    adc_params = [param for param in numeric_params if "adc" in param.lower()]

    for param in numeric_params:
        if param in temp_params or param in adc_params:
            continue  # skip solar temp and adc params; they'll be handled below

        df_clean[param] = pd.to_numeric(df_clean[param], errors="coerce")
        valid_data = df_clean[["groundTime", "In memory of", param]].dropna(subset=[param])
        valid_data = valid_data.sort_values("groundTime")

        if len(valid_data) > 1 and valid_data[param].nunique() > 1:
            trace = go.Scatter(
                x=list(pd.array(valid_data["groundTime"])),
                y=list(pd.array(valid_data[param])),
                mode="lines+markers",
                name=param,
                text=valid_data["In memory of"],
                hovertemplate=(
                    f"<b>%{{x|%Y-%m-%d %H:%M:%S}}</b><br>{param}: %{{y}}<br>In memory of: %{{text}}<extra></extra>"
                ),
                line_shape="linear"
            )

            layout = go.Layout(
                title=param,
                template="plotly_white",
                height=350,
                xaxis=dict(title="Time", type="date"),
                yaxis=dict(title=param),
                margin=dict(t=50, b=40, l=20, r=20)
            )

            fig = go.Figure(data=[trace], layout=layout)
            section_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            other_sections.append(section_html)

    # === Plot all solar panel temperature readings in one plot ===
    if temp_params:
        traces = []
        for param in temp_params:
            df_clean[param] = pd.to_numeric(df_clean[param], errors="coerce")
            valid_data = df_clean[["groundTime", "In memory of", param]].dropna(subset=[param])
            valid_data = valid_data.sort_values("groundTime")

            if len(valid_data) > 1 and valid_data[param].nunique() > 1:
                trace = go.Scatter(
                    x=list(pd.array(valid_data["groundTime"])),
                    y=list(pd.array(valid_data[param])),
                    mode="lines+markers",
                    name=param,
                    text=valid_data["In memory of"],
                    hovertemplate=(
                        f"<b>%{{x|%Y-%m-%d %H:%M:%S}}</b><br>{param}: %{{y}}<br>In memory of: %{{text}}<extra></extra>"
                    ),
                    line_shape="linear"
                )
                traces.append(trace)

        if traces:
            layout = go.Layout(
                title="Solar Panel Temperatures",
                template="plotly_white",
                height=400,
                xaxis=dict(title="Time", type="date"),
                yaxis=dict(title="Temperature"),
                margin=dict(t=50, b=40, l=20, r=20)
            )
            fig = go.Figure(data=traces, layout=layout)
            section_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            other_sections.append(section_html)

    # === Plot all ADC channels in one plot ===
    if adc_params:
        traces = []
        for param in adc_params:
            df_clean[param] = pd.to_numeric(df_clean[param], errors="coerce")
            valid_data = df_clean[["groundTime", "In memory of", param]].dropna(subset=[param])
            valid_data = valid_data.sort_values("groundTime")

            if len(valid_data) > 1 and valid_data[param].nunique() > 1:
                trace = go.Scatter(
                    x=list(pd.array(valid_data["groundTime"])),
                    y=list(pd.array(valid_data[param])),
                    mode="lines+markers",
                    name=param,
                    text=valid_data["In memory of"],
                    hovertemplate=(
                        f"<b>%{{x|%Y-%m-%d %H:%M:%S}}</b><br>{param}: %{{y}}<br>In memory of: %{{text}}<extra></extra>"
                    ),
                    line_shape="linear"
                )
                traces.append(trace)

        if traces:
            layout = go.Layout(
                title="ADC Channels",
                template="plotly_white",
                height=400,
                xaxis=dict(title="Time", type="date"),
                yaxis=dict(title="ADC Value"),
                margin=dict(t=50, b=40, l=20, r=20)
            )
            fig = go.Figure(data=traces, layout=layout)
            section_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            other_sections.append(section_html)
    for param in numeric_params:
        if param in temp_params:
            continue  # skip solar temp params since they are already plotted together

        df_clean[param] = pd.to_numeric(df_clean[param], errors="coerce")
        valid_data = df_clean[["groundTime", "In memory of", param]].dropna(subset=[param])
        valid_data = valid_data.sort_values("groundTime")

        if len(valid_data) > 1 and valid_data[param].nunique() > 1:
            trace = go.Scatter(
                x=list(pd.array(valid_data["groundTime"])),
                y=list(pd.array(valid_data[param])),
                mode="lines+markers",
                name=param,
                text=valid_data["In memory of"],
                hovertemplate=(
                    f"<b>%{{x|%Y-%m-%d %H:%M:%S}}</b><br>{param}: %{{y}}<br>In memory of: %{{text}}<extra></extra>"
                ),
                line_shape="linear"
            )

            layout = go.Layout(
                title=param,
                template="plotly_white",
                height=350,
                xaxis=dict(title="Time", type="date"),
                yaxis=dict(title=param),
                margin=dict(t=50, b=40, l=20, r=20)
            )

            fig = go.Figure(data=[trace], layout=layout)
            section_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            other_sections.append(section_html)

    html_sections = other_sections + html_sections  # Place solar & ADC plots last
    column1 = html_sections[::2]
    column2 = html_sections[1::2]

    # Get latest dedication info
    latest_record = df_clean.dropna(subset=["In memory of"]).sort_values("groundTime", ascending=False).iloc[0]
    latest_in_memory_of = latest_record["In memory of"]
    latest_ground_time = latest_record["groundTime"].strftime("%Y-%m-%d %H:%M:%S")

    # === Compose final HTML ===
    html_full = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <title>🛰️ Tevel-2 Telemetry</title>
        <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f4f6f9;
                margin: 0;
                padding: 0;
            }}
            header {{
                text-align: center;
                padding: 40px 20px 20px;
                background: #ffffff;
                box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.04);
            }}
            h1 {{
                margin: 0;
                font-size: 32px;
            }}
            .container {{
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                max-width: 1300px;
                margin: 30px auto;
                gap: 20px;
                padding: 0 20px 40px;
            }}
            .column {{
                width: 48%;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            .card {{
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
            }}
            .memorial {{
                max-width: 600px;
                margin: 0 auto 20px;
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
                text-align: center;
            }}
            .memorial h4 {{
                margin: 0 0 10px;
            }}
            .memorial .name {{
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }}
            .memorial .time {{
                font-size: 14px;
                color: #777;
                margin-top: 6px;
            }}
            @media (max-width: 768px) {{
                .column {{
                    width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>🛰️ Tevel-2 Telemetry</h1>
        </header>
    
        <div class=\"memorial\">
            <h4>In memory of:</h4>
            <div class=\"name\">{latest_in_memory_of}</div>
            <div class=\"time\">Ground time: {latest_ground_time}</div>
        </div>
    
        <div class=\"container\">
            <div class=\"column\">
                {''.join(f'<div class=\"card\">{plot}</div>' for plot in column1)}
            </div>
            <div class=\"column\">
                {''.join(f'<div class=\"card\">{plot}</div>' for plot in column2)}
            </div>
        </div>
    </body>
    </html>
    """

    # Save to file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_full)

    print("✅ Saved to tevel2_static_dashboard_fixed.html")

import subprocess

def git_commit_and_push(commit_message="Auto update"):
    from github import Github

    with open("github_token.txt", "r") as f:
        token2 = f.read().strip()

    # Auth with token
    g = Github(token2)

    # Get repo
    repo = g.get_repo("ohadshapira/tevel2")

    file_path = "index.html"
    # Read your file and push it
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        file = repo.get_contents(file_path, ref="main")  # adjust branch if needed
        sha = file.sha

        # Update the file
        repo.update_file(
            path=file_path,
            message="Update dashboard HTML",
            content=content,
            sha=sha,
            branch="main"
        )
        print("✅ File updated on GitHub.")
    except Exception as e:
        print("❌ Error:", e)

    print("✅ File uploaded to GitHub!")

    # try:
    #     # Add all changes
    #     subprocess.run(["git", "add", "index.html"], check=True)
    #
    #     # Commit with message
    #     subprocess.run(["git", "commit", "-m", commit_message], check=True)
    #
    #     # Push to the current branch
    #     subprocess.run(["git", "push"], check=True)
    #
    #     print("✅ Git changes committed and pushed.")
    #
    # except subprocess.CalledProcessError as e:
    #     print("❌ Git operation failed:", e)


wait_time_s=60
while True:
    try:
        print("⏳ Generating dashboard...")
        data = get_all_documents()
        generate_html(data)
        git_commit_and_push()
        print(f"✅ Dashboard updated. Waiting {wait_time_s} seconds...\n")
        time.sleep(wait_time_s)
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    except Exception as e:
        print(e)
