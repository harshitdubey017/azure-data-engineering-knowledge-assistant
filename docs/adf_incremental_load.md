# ADF Incremental Data Loading

## Overview
Incremental loading processes only new or changed records rather than repeatedly processing the entire source.

## Watermark Pattern
A watermark represents the last successfully processed point. Common watermark columns are timestamps, increasing IDs, or sequence numbers.

```sql
SELECT *
FROM source_table
WHERE last_modified > :previous_watermark
  AND last_modified <= :current_watermark;
```

## Workflow
1. Read the previous successful watermark.
2. Determine the current watermark.
3. Extract the incremental range.
4. Land the data.
5. Validate the load.
6. Transform or upsert.
7. Advance the watermark only after successful processing.

## CDC
Change Data Capture can identify inserts, updates, and deletes for incremental processing.

## Idempotency
Rerunning the same window should not create incorrect duplicates. Common techniques include MERGE, deterministic keys, deduplication, and processed-file tracking.

## Example
Previous watermark: 2026-01-10 10:00:00
Current watermark: 2026-01-10 11:00:00

Process records where `updated_at` is greater than the previous value and less than or equal to the current value.
