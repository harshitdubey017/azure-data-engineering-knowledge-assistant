# SQL Optimization for Data Engineering

## Overview
SQL optimization reduces query execution time and resource consumption while preserving correctness.

## Projection and Filtering
Select only required columns and filter data as early as practical.

```sql
SELECT customer_id, order_date, amount
FROM orders
WHERE order_date >= '2026-01-01';
```

## Joins
Choose appropriate join types and understand the volume and distribution on both sides.

Common joins include INNER, LEFT, RIGHT, and FULL OUTER JOIN.

## Window Functions
Window functions are useful for deduplication, latest-record selection, ranking, running totals, and change detection.

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC
)
```

## Incremental Processing
For large datasets, process only the required time or key range when supported by the architecture.

## Data Quality
SQL can validate nulls, duplicates, referential integrity, row-count reconciliation, ranges, and business rules.

## Optimization Checklist
1. Inspect the execution plan.
2. Reduce data scanned.
3. Filter early.
4. Select required columns.
5. Review joins.
6. Check skew.
7. Check partition pruning where applicable.
8. Avoid repeated computation.
