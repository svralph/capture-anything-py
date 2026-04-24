from typing import ClassVar, Final, Mapping, Optional, Sequence, Tuple
import os

from typing_extensions import Self
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.generic import *
from viam.utils import ValueTypes
from datetime import datetime

from viam.app.data_client import DataClient
from viam.app.viam_client import ViamClient


class MetricsCapture(Generic, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("sab-viam", "capture-anything-py"), "metrics-capture"
    )

    data_client: Optional[DataClient] = None
    viam_client: Optional[ViamClient] = None

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any required dependencies or optional dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies and the
                second element is a list of optional dependencies
        """
        return [], []

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
    # Ensure there is only one viam_client connection
        if not self.viam_client:
            self.viam_client = await ViamClient.create_from_env_vars()

        self.data_client = self.viam_client.data_client

        time_requested = datetime(2026, 4, 24, 11, 0, 0)
        time_received = datetime(2026, 4, 24, 11, 0, 3)

        file_id = await self.data_client.tabular_data_capture_upload(
            part_id="6847ee1a-46fe-4593-b891-78f455052b1c",
            component_type='rdk:component:movement_sensor',
            component_name='my_movement_sensor',
            method_name='Readings',
            tags=["metrics_data"],
            data_request_times=[(time_requested, time_received)],
            tabular_data=[{
                'readings': {
                    'linear_velocity': {'x': 0.5, 'y': 0.0, 'z': 0.0},
                    'angular_velocity': {'x': 0.0, 'y': 0.0, 'z': 0.1}
                }
            }]
        )

        return {file_id: file_id}

    async def get_status(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, ValueTypes]:
        self.logger.error("`get_status` is not implemented")
        raise NotImplementedError()

