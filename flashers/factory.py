import sys
from pathlib import Path
from flashers.esp import ESPFlasher
from flashers.avr import AVRFlasher

def get_base_path():
    """Get the base path whether running as script or packaged exe"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def create_flasher(target, chip=None):
    """
    Create a flasher instance for the given target.
    
    Args:
        target: The target platform ("espressif", "esp32", "esp8266", "avr")
        chip: For ESP targets, the specific chip (esp32, esp32s3, esp8266, etc.)
    """
    
    base_path = get_base_path()
    
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
        avrdude_path = str(base_path / "tools" / "avrdude.exe")
        avrdude_conf = str(base_path / "tools" / "avrdude.conf")
        
        # Check if files exist, try system PATH as fallback
        if not Path(avrdude_path).exists():
            import shutil
            system_avrdude = shutil.which("avrdude")
            if system_avrdude:
                avrdude_path = system_avrdude
                # Try to find avrdude.conf in standard locations
                possible_conf_paths = [
                    base_path / "tools" / "avrdude.conf",
                    Path("C:/Program Files/avrdude/avrdude.conf"),
                    Path("C:/avrdude/avrdude.conf")
                ]
                for conf_path in possible_conf_paths:
                    if conf_path.exists():
                        avrdude_conf = str(conf_path)
                        break
        
        return AVRFlasher(avrdude_path, avrdude_conf)
    
    else:
        raise ValueError(f"Unsupported target: {target}")