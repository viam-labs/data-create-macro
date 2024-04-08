import json
import os

VIAM_PATH = "~/.viam/capture"
SERVICE_NAME = "data"


class Config:

    config = {str: any}
    component_types_to_count = {str: int}

    def __init__(self, robot_id: str) -> None:
        self.config = {
            "components": [],
            "services": [
                {
                    "name": SERVICE_NAME,
                    "type": "data_manager",
                    "namespace": "rdk",
                    "attributes": {
                        "sync_interval_mins": 0.1,
                        "capture_dir": f"{VIAM_PATH}/{robot_id}",
                        "tags": [],
                        "additional_sync_paths": [],
                    },
                }
            ],
        }

    def add_arm(self, frequency=1) -> None:
        name = self.get_new_name("arm")

        self.config["components"].append(
            {
                "name": name,
                "namespace": "rdk",
                "type": "arm",
                "model": "fake",
                "attributes": {},
                "depends_on": [],
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "JointPositions",
                                    "capture_frequency_hz": frequency,
                                },
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "EndPosition",
                                },
                            ]
                        },
                    }
                ],
            }
        )

    def add_encoder(self, frequency=1) -> None:
        name = self.get_new_name("encoder")

        self.config["components"].append(
            {
                "namespace": "rdk",
                "type": "encoder",
                "model": "fake",
                "attributes": {},
                "depends_on": [],
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "TicksCount",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                }
                            ]
                        },
                    }
                ],
                "name": name,
            },
        )

    def add_gantry(self, frequency=1) -> None:
        name = self.get_new_name("gantry")
        self.config["components"].append(
            {
                "attributes": {},
                "depends_on": [],
                "name": name,
                "service_configs": [
                    {
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "Position",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                                {
                                    "method": "Lengths",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                            ]
                        },
                        "type": "data_manager",
                    }
                ],
                "namespace": "rdk",
                "type": "gantry",
                "model": "fake",
            }
        )

    def add_motor(self, frequency=1) -> None:
        name = self.get_new_name("motor")

        self.config["components"].append(
            {
                "model": "fake",
                "attributes": {},
                "depends_on": [],
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "IsPowered",
                                    "additional_params": {},
                                }
                            ]
                        },
                    }
                ],
                "name": name,
                "namespace": "rdk",
                "type": "motor",
            }
        )

    def add_movement_sensor(self, frequency=1) -> None:
        name = self.get_new_name("movement_sensor")

        self.config["components"].append(
            {
                "type": "movement_sensor",
                "model": "fake",
                "attributes": {},
                "depends_on": [],
                "name": name,
                "namespace": "rdk",
                "service_configs": [
                    {
                        "attributes": {
                            "capture_methods": [
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "Readings",
                                    "additional_params": {},
                                },
                                {
                                    "method": "AngularVelocity",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                                {
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                    "method": "CompassHeading",
                                },
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "LinearAcceleration",
                                    "additional_params": {},
                                },
                                {
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                    "method": "LinearVelocity",
                                },
                                {
                                    "method": "Orientation",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                                {
                                    "method": "Position",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                            ]
                        },
                        "type": "data_manager",
                    }
                ],
            }
        )

    def add_power_sensor(self, frequency=1) -> None:
        name = self.get_new_name("power_sensor")

        self.config["components"].append(
            {
                "model": "fake",
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "Readings",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                },
                                {
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                    "method": "Voltage",
                                },
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "Current",
                                    "additional_params": {},
                                },
                                {
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                    "method": "Power",
                                },
                            ]
                        },
                    }
                ],
                "attributes": {},
                "depends_on": [],
                "name": name,
                "namespace": "rdk",
                "type": "power_sensor",
            }
        )

    def add_servo(self, frequency=1) -> None:
        name = self.get_new_name("servo")

        self.config["components"].append(
            {
                "type": "servo",
                "model": "fake",
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "Position",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                }
                            ]
                        },
                    }
                ],
                "attributes": {},
                "depends_on": [],
                "name": name,
                "namespace": "rdk",
            }
        )

    def add_sensor(self, frequency=1) -> None:
        name = self.get_new_name("sensor")

        self.config["components"].append(
            {
                "model": "fake",
                "type": "sensor",
                "namespace": "rdk",
                "attributes": {},
                "depends_on": [],
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "method": "Readings",
                                    "additional_params": {},
                                    "capture_frequency_hz": frequency,
                                }
                            ]
                        },
                    }
                ],
                "name": name,
            }
        )

    def add_camera(self, frequency=1) -> None:
        name = self.get_new_name("camera")

        self.config["components"].append(
            {
                "attributes": {},
                "depends_on": [],
                "service_configs": [
                    {
                        "type": "data_manager",
                        "attributes": {
                            "capture_methods": [
                                {
                                    "capture_frequency_hz": frequency,
                                    "method": "ReadImage",
                                    "additional_params": {"mime_type": "image/jpeg"},
                                }
                            ]
                        },
                    }
                ],
                "name": name,
                "namespace": "rdk",
                "type": "camera",
                "model": "fake",
            }
        )

    def write_config(self) -> None:
        with open("test.json", "w") as f:
            f.write(json.dumps(self.config))

    def get_new_name(self, component_type: str) -> str:
        self.component_types_to_count[component_type] = (
            self.component_types_to_count.get(component_type, 0) + 1
        )
        return f"{component_type}-{self.component_types_to_count[component_type]}"

    def showSelf(self) -> str:
        print(self.asdf)
