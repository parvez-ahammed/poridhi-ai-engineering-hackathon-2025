# Observability Framework for Search Engine

The following diagram illustrates the observability framework for the search engine, including metrics, logs, traces, and alerts. Each section is further broken down into specific tools and dashboards used for monitoring and analysis.

```mermaid
graph LR
    A[Observability Framework] --> B[Grafana]

    B --> C[Metrics]
    B --> D[Logs]
    B --> E[Traces]
    B --> F[Alerts]
    B --> G[Performance Tests]

    %% Metrics Section
    C --> C1[Prometheus]
    C1 --> C1a[Collected Metrics: \n• Latency \n• Throughput \n• Error Rates \n• Indexing Performance \n• Response Time \n• Cache Hit/Miss \n• Resource Usage]
    C1 --> C1b[Dashboards]
    C1b --> Dm1[Request Metrics Dashboard]
    C1b --> Dm2[Search Performance Dashboard]
    C1b --> Dm3[Cache Efficiency Dashboard]
    C1b --> Dm4[System Resource Dashboard]
    C1b --> Dm5[Indexing Stats Dashboard]

    %% Logs Section
    D --> D1[Loki]
    D1 --> D1a[Log Types: \n• Request Logs \n• Search Logs \n• Error Logs \n• Index Logs]
    D1 --> D1b[Dashboards]
    D1b --> Dl1[Error Log Dashboard]
    D1b --> Dl2[Search Logs Dashboard]
    D1b --> Dl3[Request Flow Log Dashboard]
    D1b --> Dl4[Index Log Dashboard]

    %% Traces Section
    E --> E1[Tracing Tools]
    E1 --> E1a[OpenTelemetry \n+ Jaeger / Zipkin]
    E1 --> E1b[Traced Data: \n• Spans \n• Dependencies \n• Latency Breakdown]
    E1 --> E1c[Dashboards]
    E1c --> Dt1[End-to-End Tracing View]
    E1c --> Dt2[Service Dependency Map]
    E1c --> Dt3[Slow Path Analysis Dashboard]

    %% Alerts Section
    F --> F1[Prometheus Alertmanager]
    F1 --> F1a[Alert Types: \n• Thresholds \n• Anomalies \n• Health Checks]
    F1 --> F1b[Dashboards]
    F1b --> Da1[Alert Overview Dashboard]
    F1b --> Da2[Incident History Dashboard]
    F1b --> Da3[Uptime & Availability Dashboard]

    %% Performance Tests
    G --> G1[K6 - Load & Stress Testing]
    G1 --> G2[Outputs: \n• RPS \n• VUs \n• Latencies \n• Errors]
    G1 --> G3[Sent to: Prometheus/InfluxDB]
    G1 --> G4[Dashboards]
    G4 --> Dk1[K6 Test Results Dashboard]
    G4 --> Dk2[Latency Distribution Dashboard]
    G4 --> Dk3[VU Load Curve Dashboard]
    G4 --> Dk4[Error Rate Trends]

```
