# Unity Catalog

## Overview
Unity Catalog provides centralized governance for data and AI assets in Databricks.

## Three-Level Namespace
A common structure is:

```text
catalog.schema.table
```

Example:

```text
analytics_prod.sales.orders
```

## Governance
Centralized governance can cover permissions, discovery, ownership, auditing, lineage, external locations, and storage credentials.

## Access Control
Apply least privilege. Users and service principals should receive only the permissions required for their workloads.

## Lineage
Lineage helps users understand upstream and downstream relationships between data assets.

## Production Considerations
Consider environment separation, catalog design, schema ownership, service principals, storage credentials, external locations, and auditability.

## Example
```text
data_prod
  raw
  curated
  analytics
```

Use centralized governance rather than distributing credentials through notebooks and pipelines.
