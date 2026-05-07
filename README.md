# Module `capture-anything-py`

`capture-anything-py` provides a generic Viam service model that accepts tabular data payloads through `DoCommand` and uploads them to Viam Data via the Python `DataClient`.

## Models

This module provides the following model(s):

- [`sab-viam:capture-anything-py:metrics-capture`](sab-viam_capture-anything-py_metrics-capture.md) - Generic service that forwards caller-provided tabular capture data to Viam Data upload APIs.

## Module configuration

This model expects a `part_id` attribute in resource configuration.

Example resource config:

```json
{
  "name": "metrics-capture-1",
  "api": "rdk:service:generic",
  "model": "sab-viam:capture-anything-py:metrics-capture",
  "attributes": {
    "part_id": "6847ee1a-46fe-4593-b891-78f455052b1c"
  }
}
```

## Using `DoCommand` with `metrics-capture`

The `sab-viam:capture-anything-py:metrics-capture` model expects callers to pass tabular upload metadata and payload through `DoCommand`. The module forwards these values to `DataClient.tabular_data_capture_upload`.

Required keys in `DoCommand` payload:

- `component_type` (`string`) - for example `rdk:component:movement_sensor`
- `component_name` (`string`) - resource name on the machine
- `method_name` (`string`) - for example `Readings`
- `tabular_data` (`array`) - list of tabular records (for sensors, include `readings`)

Optional keys:

- `tags` (`array[string]`) - defaults to `[]`
- `data_request_times` (`array[[requested_time, received_time]]`) - ISO 8601 timestamp string pairs. If omitted, timestamps default to the current time.

Example `DoCommand` payload:

```json
{
  "component_type": "rdk:component:movement_sensor",
  "component_name": "my_movement_sensor",
  "method_name": "Readings",
  "tags": ["metrics_data"],
  "data_request_times": [
    ["2026-05-07T17:00:00Z", "2026-05-07T17:00:01Z"]
  ],
  "tabular_data": [
    {
      "readings": {
        "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
        "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
      }
    }
  ]
}
```

## Example caller usage (Python)

```python
payload = {
    "component_type": "rdk:component:movement_sensor",
    "component_name": "my_movement_sensor",
    "method_name": "Readings",
    "tags": ["metrics_data"],
    "data_request_times": [
        ["2026-05-07T17:00:00Z", "2026-05-07T17:00:01Z"]
    ],
    "tabular_data": [
        {
            "readings": {
                "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
                "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
            }
        }
    ]
}

result = await metrics_capture_service.do_command(payload)
file_id = result["file_id"]
```
