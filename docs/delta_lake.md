# Delta Lake

## Overview
Delta Lake is a transactional storage layer that adds reliability and data management capabilities to data lakes.

## Capabilities
- ACID transactions
- Schema enforcement
- Schema evolution
- Time travel
- MERGE
- UPDATE
- DELETE
- Change Data Feed
- Transaction history

## MERGE
MERGE is commonly used for incremental upserts.

```sql
MERGE INTO target t
USING source s
ON t.business_key = s.business_key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

## Time Travel
Transaction history can allow historical versions of a table to be queried or restored.

## Change Data Feed
Change Data Feed can expose row-level changes between table versions for downstream incremental processing.

## Small Files
Frequent small writes can create many files. Compaction and appropriate write strategies can improve read performance.

## VACUUM
VACUUM removes files no longer required according to retention settings. Retention should be handled carefully because it affects historical availability.

## Medallion Architecture
Bronze commonly contains ingested data, Silver contains cleaned/conformed data, and Gold contains business-ready datasets.
