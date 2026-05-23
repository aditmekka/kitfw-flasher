from pathlib import Path
import subprocess
import time

from flashers.base import BaseFlasher

class AVRFlasher(BaseFlasher):

    MCU = "atmega328p"
    PROGRAMMER = "arduino"

    def __init__(self, avrdude_path: str, avrdude_conf: str):
        self.avrdude_path = avrdude_path
        self.avrdude_conf = avrdude_conf
        self.process = None

    def build_command(self, port: str, baud: int, firmware_path: Path) -> list[str]:
        return [
            self.avrdude_path,
            "-C", self.avrdude_conf,
            f"-p{self.MCU}",
            f"-c{self.PROGRAMMER}",
            f"-P{port}",
            f"-b{baud}",
            "-D",
            f"-Uflash:w:{firmware_path}:i"
        ]

    def _run_command(self, cmd: list[str], log_callback=None) -> bool:
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        try:
            if self.process.stdout:
                while True:
                    ch = self.process.stdout.read(1)
                    if not ch:
                        break
                    
                    if log_callback:
                        log_callback(ch)
                    else:
                        print(ch, end="", flush=True)
            
            self.process.wait()
            return self.process.returncode == 0
            
        finally:
            self.process = None

    def flash(self, port: str, package_dir, manifest, log_callback=None):
        if not manifest.flash:
            raise RuntimeError("Manifest contains no firmware entries")

        firmware_path = Path(package_dir) / manifest.flash[0].file

        if not firmware_path.exists():
            raise FileNotFoundError(f"Firmware not found: {firmware_path}")

        baud_rates = [115200, 57600]  # Nano new bootloader, Nano old bootloader

        for baud in baud_rates:
            status_msg = f"Trying upload at {baud} baud...\n"
            if log_callback:
                log_callback(status_msg)
            else:
                print(status_msg, end="")

            cmd = self.build_command(port, baud, firmware_path)
            success = self._run_command(cmd, log_callback)

            if success:
                success_msg = f"Upload successful ({baud} baud)\n"
                if log_callback:
                    log_callback(success_msg)
                else:
                    print(success_msg, end="")
                return

            fail_msg = f"Upload failed ({baud} baud)\n"
            if log_callback:
                log_callback(fail_msg)
            else:
                print(fail_msg, end="")

        raise RuntimeError("Upload failed using all baud rates")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(0.5)
            if self.process.poll() is None:
                self.process.kill()