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
