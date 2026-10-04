# Azure Databricks Best Practices

## Overview
Azure Databricks provides a managed environment for distributed data processing, analytics, and data engineering.

## Notebook Practices
- Keep notebooks focused.
- Move reusable logic into modules where appropriate.
- Parameterize environment-specific values.
- Never embed secrets.
- Document assumptions and dependencies.

## Distributed Processing
Avoid collecting large datasets to the driver with operations such as `collect()` or `toPandas()`.

## Partitioning
Choose partitioning based on access patterns and cardinality. Excessive partitioning can create small files; insufficient partitioning can reduce parallelism.

## Joins
Broadcast joins can avoid a large shuffle when one side is appropriately small. Large-to-large joins may require shuffle and should be evaluated using execution plans.

## Delta Lake
Use Delta capabilities such as MERGE, UPDATE, DELETE, schema enforcement, schema evolution, and transaction history appropriately.

## Security
Use managed identities, service principals, secure secret management, Unity Catalog permissions, and least-privilege access.

## Production
Monitor failures, runtime, data volume, cluster behavior, shuffle, and data quality.

## Cost Optimization
Use suitable cluster sizing, efficient storage formats, appropriate job clusters, and avoid unnecessary computation.
