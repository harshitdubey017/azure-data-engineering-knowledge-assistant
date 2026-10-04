# Spark Performance Optimization

## Lazy Evaluation
Spark transformations are evaluated lazily. Actions trigger execution.

Transformations include select, filter, join, groupBy, and withColumn. Actions include count, show, collect, and write.

## Shuffle
Shuffle redistributes data across executors. Common shuffle operations include groupBy, join, distinct, orderBy, and repartition.

## Repartition vs Coalesce
`repartition()` redistributes data and can increase or decrease partitions, generally causing a shuffle. `coalesce()` is commonly used to reduce partitions with less movement.

## Broadcast Join
Broadcast joins send a small dataset to executors and can avoid a large shuffle. Use only when the dataset is small enough for available executor memory.

## Data Skew
Data skew occurs when some partitions contain much more data than others. Symptoms include a few tasks running substantially longer than the rest.

Possible techniques include salting, improved partitioning, broadcast joins, filtering, and changing join strategy.

## Caching
Cache data when it is reused. Caching one-time datasets can waste memory.

## File Optimization
Prefer Parquet or Delta and avoid excessive small files.

## Execution Plans
Inspect execution plans for joins, exchanges, filters, scans, and sorts. Optimize based on measured execution behavior.
