import asyncio
from viam.module.module import Module
from models.metrics_capture import MetricsCapture as MetricsCaptureModel


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
