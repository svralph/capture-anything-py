# Module `capture-anything-py`

`capture-anything-py` provides a generic Viam service model that accepts tabular data payloads through `DoCommand` and uploads them to Viam Data via the Python `DataClient`.

## Models

This module provides the following model(s):

- [`sab-viam:capture-anything-py:metrics-capture`](sab-viam_capture-anything-py_metrics-capture.md) - Generic service that forwards caller-provided tabular capture data to Viam Data upload APIs.

## Module configuration

This model does not require a `part_id` attribute. It automatically retrieves `robot_part_id` from Viam cloud metadata at runtime.

Example resource config:

```json
{
  "name": "metrics-capture-1",
  "api": "rdk:service:generic",
  "model": "sab-viam:capture-anything-py:metrics-capture"
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

Empty template:

```json
{
  "component_type": "",
  "component_name": "",
  "method_name": "",
  "tags": [],
  "data_request_times": [
    ["", ""]
  ],
  "tabular_data": [
    {
      "readings": {}
    }
  ]
}
```

## Example caller usage from another Viam module (Python)

```python
from datetime import datetime, timezone

# Example: your module already has a movement sensor client and a reference
# to this metrics-capture generic service.
readings = await movement_sensor.get_readings()
requested = datetime.now(timezone.utc)
received = datetime.now(timezone.utc)

upload_payload = {
    "component_type": movement_sensor.get_resource_name().resource_namespace,
    "component_name": movement_sensor.get_resource_name().name,
    "method_name": "Readings",
    "tags": ["metrics_data", "from_my_module"],
    "data_request_times": [[requested.isoformat(), received.isoformat()]],
    "tabular_data": [{"readings": readings}],
}

result = await metrics_capture_service.do_command(upload_payload)
file_id = result["file_id"]
```
