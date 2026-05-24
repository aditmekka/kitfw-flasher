from flashers.esp import ESPFlasher
from flashers.avr import AVRFlasher

def create_flasher(target, chip=None):
    """
    Create a flasher instance for the given target.
    
    Args:
        target: The target platform ("espressif", "esp32", "esp8266", "avr")
        chip: For ESP targets, the specific chip (esp32, esp32s3, esp8266, etc.)
    """
    
    # Handle ESP targets
    if target == "espressif":
        if not chip:
            raise ValueError("Chip type required for espressif target")
        

        if chip.startswith("esp"):
            return ESPFlasher(chip)
        else:
            raise ValueError(f"Unsupported chip for espressif: {chip}")
    
    # Legacy support for old packages that use "esp32" or "esp8266" directly
    elif target in ["esp32", "esp8266"]:
        return ESPFlasher(target)
    
    # Handle AVR target
    elif target == "avr":
        return AVRFlasher(
            avrdude_path="tools/avrdude.exe",
            avrdude_conf="tools/avrdude.conf"
        )
    
    else:
        raise ValueError(f"Unsupported target: {target}")