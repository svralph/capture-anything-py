import os

from typing import ClassVar, Mapping, Optional, Sequence, Tuple, Any, List

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
from viam.robot.client import RobotClient


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
        self = super().new(config, dependencies)
        return self

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

        part_id = os.environ.get("VIAM_MACHINE_PART_ID")

        component_name = command.get("component_name")
        tags = command.get("tags", [])
        tabular_data = command.get("tabular_data")

        if not isinstance(component_name, str) or not component_name:
            raise ValueError("`component_name` must be a non-empty string")
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            raise ValueError("`tags` must be a list of strings")
        if not isinstance(tabular_data, list) or len(tabular_data) == 0:
            raise ValueError("`tabular_data` must be a non-empty list")

        raw_data_request_times = command.get("data_request_times")
        data_request_times: List[Tuple[datetime, datetime]] = []

        if raw_data_request_times is None:
            now = datetime.now()
            data_request_times = [(now, now)] * len(tabular_data)
        else:
            if not isinstance(raw_data_request_times, list):
                raise ValueError("`data_request_times` must be a list")
            for item in raw_data_request_times:
                if (
                    not isinstance(item, list)
                    and not isinstance(item, tuple)
                ) or len(item) != 2:
                    raise ValueError(
                        "`data_request_times` must be a list of [requested_time, received_time]"
                    )
                requested_time_raw, received_time_raw = item
                if not isinstance(requested_time_raw, str) or not isinstance(received_time_raw, str):
                    raise ValueError("timestamps in `data_request_times` must be ISO 8601 strings")
                data_request_times.append(
                    (
                        datetime.fromisoformat(requested_time_raw.replace("Z", "+00:00")),
                        datetime.fromisoformat(received_time_raw.replace("Z", "+00:00")),
                    )
                )

        readings = {}
        for item in tabular_data:
            for key in item.keys():
                readings[key] = item[key]
        print(f"readings: {readings}")

        file_id = await self.data_client.tabular_data_capture_upload(
            part_id=part_id,
            component_type="rdk:component:sensor",
            component_name=component_name,
            method_name="Readings",
            tags=tags,
            data_request_times=data_request_times,
            tabular_data={"readings": readings},
        )

        return {"file_id": file_id}

    async def get_status(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, ValueTypes]:
        self.logger.error("`get_status` is not implemented")
        raise NotImplementedError()

