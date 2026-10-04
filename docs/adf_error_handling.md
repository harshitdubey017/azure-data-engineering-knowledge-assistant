# ADF Error Handling

## Common Failures
- Connectivity failure
- Authentication failure
- Schema mismatch
- Missing file
- Invalid data
- Transformation failure
- Timeout
- Dependency failure
- Destination write failure

## Dependency Conditions
ADF can branch on Success, Failure, Completion, and Skipped outcomes.

```text
Main Activity
  |-- Success --> Validation --> Continue
  |-- Failure --> Log Error --> Alert
```

## Retry
Use retries for transient failures such as temporary network or service issues. Do not use retries as a substitute for fixing deterministic failures.

## Logging
Capture pipeline name, run ID, activity, start/end time, error message, source, target, and row counts.

## Safe Reruns
Use idempotent transformations, staging, MERGE/upsert, run-specific paths, processed-record tracking, and watermark control.

## Troubleshooting
Identify the failed run, locate the failed activity, inspect the detailed error, classify the failure, validate source/destination and schema, correct the cause, rerun the required scope, and validate the output.
