# Troubleshooting High Latency

Symptoms: p99 latency on the retrieval service climbs above 2 seconds, and
users report slow answers.

## Likely Causes

### Vector Index Not Warmed

If the service was recently restarted, the in-memory index cache may still
be cold. This typically resolves itself within a few minutes as traffic
warms the cache.

### Oversized Chunks

If recently ingested documents were chunked with an unusually large chunk
size, retrieval has to embed and compare larger passages, which increases
latency. Check the ingestion config for the affected document set.

### Downstream Model Latency

The answer service depends on an external language model API. If that API
is degraded, retrieval latency will look normal but overall response time
will still be high. Check the answer service's dashboards separately.

## Mitigation

Restart the retrieval service to force a fresh index load, and check recent
ingestion runs for configuration changes before escalating.
