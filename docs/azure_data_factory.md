# Azure Data Factory

## Overview
Azure Data Factory (ADF) is a cloud data integration and orchestration service used to build, schedule, monitor, and manage data workflows.

## Core Components
- Pipeline: logical workflow container.
- Activity: individual operation inside a pipeline.
- Dataset: describes data used by an activity.
- Linked Service: connection information for external systems.
- Integration Runtime: compute/connectivity infrastructure.
- Trigger: starts a pipeline.
- Parameters and Variables: support reusable and dynamic workflows.

## Metadata-Driven Pipelines
A metadata-driven framework stores configuration such as source, target, load type, watermark column, and destination. A generic pipeline reads the configuration and executes the required workflow.

Benefits include reduced duplication, centralized configuration, easier onboarding, and consistent operational handling.

## Common Pattern
Source -> ADF Copy Activity -> ADLS Gen2 -> Databricks Transformation -> Delta Lake -> Data Quality -> Consumer

## Monitoring
Monitor pipeline status, activity failures, duration, retries, row counts, dependencies, and data-quality results.

## Best Practices
- Parameterize reusable pipelines.
- Avoid hard-coded secrets.
- Use Key Vault or managed identity.
- Implement retry and failure paths.
- Log useful operational metadata.
- Design safe reruns.
- Separate environment-specific configuration.
