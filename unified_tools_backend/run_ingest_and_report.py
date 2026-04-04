from ingestion_pipeline import IngestionPipeline
from monitor_backend import write_monitor_report, get_monitor_report

# Instantiate pipeline and ingest same test events
pipeline = IngestionPipeline()

# Single event (3 replays)
for _ in range(3):
    pipeline.ingest_event(
        source_url="https://example.com/news/weather",
        raw_content="IMD predicts normal monsoon in 2026. Rainfall expected to be normal.",
        registry_reference_id="REG_WEATHER_2026_03",
        location="India",
        sources=[{"source_id":"imd","is_institutional":True,"authority_score":0.92}]
    )

# Batch events
batch_events = [
    {
        "source_url": f"https://source{i}.com/news/{i}",
        "raw_content": f"News event {i} with deterministic content",
        "registry_reference_id": f"REG_TEST_2026_0{i}",
        "location": ["India", "US", "China", "UK", "Japan"][i % 5]
    }
    for i in range(1,6)
]

for event in batch_events:
    pipeline.ingest_event(
        source_url=event["source_url"],
        raw_content=event["raw_content"],
        registry_reference_id=event["registry_reference_id"],
        location=event.get("location", None)
    )

# Write monitor report
path = write_monitor_report('monitor_report.json')
print(path)
print(get_monitor_report())
