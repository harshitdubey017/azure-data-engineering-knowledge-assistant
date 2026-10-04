# PySpark

## Overview
PySpark is the Python API for Apache Spark and is commonly used for distributed data processing.

## DataFrame
A Spark DataFrame is a distributed collection of data organized into named columns.

```python
df = spark.read.format("delta").load(path)

result = (
    df.filter("status = 'ACTIVE'")
      .select("customer_id", "amount")
)
```

## Transformations
Common transformations include select, filter, join, groupBy, withColumn, and dropDuplicates.

## Actions
Common actions include count, show, collect, and write.

## Window Functions
Window functions support deduplication, ranking, running totals, and change detection. Common functions include row_number, rank, dense_rank, lag, and lead.

## Deduplication
A common pattern uses `row_number()` partitioned by a business key and ordered by an update timestamp.

## Joins
Join performance depends on dataset size, join keys, distribution, partitioning, and broadcast eligibility.

## Best Practices
- Select only required columns.
- Filter early where practical.
- Avoid unnecessary actions.
- Avoid collecting large datasets to the driver.
- Choose join strategies deliberately.
- Inspect execution plans.
- Use efficient storage formats.
