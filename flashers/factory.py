import sys
from pathlib import Path
import shutil
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
        # Try multiple locations for avrdude
        possible_paths = [
            base_path / "tools" / "avrdude" / "avrdude.exe",
            base_path / "tools" / "avrdude.exe",
            Path("C:/Program Files/avrdude/avrdude.exe"),
            Path("C:/avrdude/avrdude.exe"),
        ]
        
        avrdude_path = None
        for path in possible_paths:
            if path.exists():
                avrdude_path = str(path)
                break
        
        if not avrdude_path:
            # Try system PATH
            import shutil
            system_avrdude = shutil.which("avrdude") or shutil.which("avrdude.exe")
            if system_avrdude:
                avrdude_path = system_avrdude
        
        if not avrdude_path:
            raise FileNotFoundError(f"avrdude.exe not found. Tried: {possible_paths}")
        
        # Find avrdude.conf in same directory as avrdude.exe
        avrdude_dir = Path(avrdude_path).parent
        avrdude_conf = str(avrdude_dir / "avrdude.conf")
        
        if not Path(avrdude_conf).exists():
            # Try common locations
            fallback_confs = [
                base_path / "tools" / "avrdude" / "avrdude.conf",
                base_path / "tools" / "avrdude.conf",
                Path("C:/Program Files/avrdude/avrdude.conf"),
            ]
            for conf in fallback_confs:
                if conf.exists():
                    avrdude_conf = str(conf)
                    break
        
        return AVRFlasher(avrdude_path, avrdude_conf)