from dataclasses import dataclass

@dataclass
class FlashEntry:
    file: str
    address: str | None = None

@dataclass
class Manifest:
    format_version: int
    name: str
    version: str
    target: str
    flash: list[FlashEntry]

def from_dict(data):

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
        flash=entries
    )