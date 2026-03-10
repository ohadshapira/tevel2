# TEVEL2 Telemetry Dashboard

This repository powers the public GitHub Pages dashboard for **TEVEL2**, a student-built satellite mission led by **Tel Aviv University** as part of the national **TEVEL 2 – Students Build Satellites** program.

The site is updated automatically whenever new telemetry is received by the ground station. It converts incoming telemetry records into interactive plots and publishes the dashboard to GitHub Pages.

## About TEVEL2

TEVEL2 is a scientific and educational nanosatellite program in which high-school students from across Israel designed, built, tested, and now operate a constellation of nine 1U CubeSats. The mission combines:

- **Scientific research** on the radiation environment in Low Earth Orbit
- **Amateur radio communications**
- **Education and outreach** through hands-on satellite development and operations

The mission is operated through a network of student-run ground stations, and the satellites were launched in March 2025. The constellation is designed to collect radiation-related telemetry and support distributed measurements across orbit.

## Memorial mission

One of the mission’s meaningful outreach and remembrance goals is commemoration.

Each telemetry beacon includes an **"In memory of"** field that carries the names of the fallen in the **7 October 2023 attack**. This dashboard preserves that memorial context alongside the technical telemetry, so every received packet is both scientific data and an act of remembrance.

## What this repository does

This repository acts as a simple telemetry publishing pipeline:

1. Reads telemetry records from MongoDB
2. Falls back to a local JSON file if the database is unavailable
3. Extracts telemetry parameters and timestamps
4. Builds interactive Plotly graphs for numeric telemetry values
5. Highlights the latest memorial dedication from the received packets
6. Regenerates `index.html`
7. Pushes the updated page to GitHub so GitHub Pages serves the latest dashboard

## Repository structure

- `tevel2.py` – main update script
- `index.html` – generated static dashboard page served by GitHub Pages

## How it works

The update script runs periodically:

- fetches all telemetry documents
- normalizes the telemetry parameters into a table
- detects numeric fields
- creates interactive Plotly charts
- groups some related values such as solar temperatures and ADC channels
- extracts the latest `"In memory of"` value
- writes the final HTML page
- updates the repository through the GitHub API

## Data format

Each telemetry record is expected to include:

- `groundTime` – time the packet was received by the ground station
- `params` – list of telemetry parameters, each with:
  - `name`
  - `value`

Example conceptual structure:

```json
{
  "groundTime": "2025-03-15T08:19:56Z",
  "params": [
    { "name": "batteryVoltage", "value": 7.8 },
    { "name": "solarPanelTemp1", "value": 21.4 },
    { "name": "In memory of", "value": "Name" }
  ]
}
