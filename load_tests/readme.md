# k6 Performance Testing

## Overview

This runs a **k6** performance test on the API endpoint to evaluate response times, failure rates, and system behavior under load.

## Requirements

1. **Install k6**:

   - **Windows**: `winget install k6 --source winget`
   - **Mac**: `brew install k6`
   - **Linux**: [Install k6](https://k6.io/docs/getting-started/installation/)

2. **Ensure the API Server** is running at the appropriate port.
3. Create a "summaries" folder to store the test results.

## Test Configuration

- **Virtual Users (VUs)**: Starts with 2 VUs, ramps up to 5, and then ramps down to 0.
- **Requests**: Iterations total with dynamic queries (randomized from a set list).
- **Thresholds**:
  - 95% of requests should complete in under 200ms.
  - Failure rate should be less than 0.1%.

## Running the Test

To run the performance test:

```bash
k6 run test.js
```

## Other scripts
From terminal
Generate shareable HTML report in local.
```
$env:K6_WEB_DASHBOARD="true"; $env:K6_WEB_DASHBOARD_EXPORT=”html-report.html” ;k6 run ./demo-script/stage.js
```
Generate live streaming report in local
```
$env:K6_WEB_DASHBOARD_PERIOD = "1s"; k6 run --out 'web-dashboard' ./demo-script/stage.js
```
Running script in cloud (Grafana) 
```
Grafana account > API key > k6 cloud login –token > k6 cloud ./demo-script/stage.js
Running test result locally → Sending end of result to Grafana →  k6 run ./demo-script/stage.js -o cloud
```
Running result from different geo-location
Other time series db like Datadog, InfluxDB, Prometheus etc

