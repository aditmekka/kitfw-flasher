from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class FlashEntry:
    file: str
    address: str | None = None

@dataclass
class AVRConfig:
    mcu: str
    programmer: str
    baud_rates: list[int]

@dataclass
class Manifest:
    format_version: int
    name: str
    version: str
    target: str
    flash: list[FlashEntry]
    avr: AVRConfig | None = None
    esp: dict | None = None

def from_dict(data):
    avr_cfg = None
    esp_cfg = None 

    if "avr" in data:
        avr_cfg = AVRConfig(
            mcu=data["avr"]["mcu"],
            programmer=data["avr"]["programmer"],
            baud_rates=data["avr"]["baud_rates"]
        )
    
    if "esp" in data:
        esp_cfg = data["esp"]

    entries = [
        FlashEntry(
            file=item["file"],
            address=item.get("address")
        )
        for item in data["flash"]
    ]

    return Manifest(
        format_version=data["format_version"],
        name=data["name"],
        version=data["version"],
        target=data["target"],
        flash=entries,
        avr=avr_cfg,
        esp=esp_cfg
    )