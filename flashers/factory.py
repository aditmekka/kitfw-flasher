from flashers.esp import ESPFlasher
from flashers.avr import AVRFlasher


def create_flasher(target):

    if target == "esp32":
        return ESPFlasher(
            chip="esp32"
        )

    if target == "esp8266":
        return ESPFlasher(
            chip="esp8266"
        )

    if target == "avr":
        return AVRFlasher(
            avrdude_path="tools/avrdude/avrdude.exe",
            avrdude_conf="tools/avrdude/avrdude.conf"
        )

    raise ValueError(
        f"Unsupported target: {target}"
    )