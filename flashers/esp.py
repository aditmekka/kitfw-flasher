from pathlib import Path
import subprocess
import time

from flashers.base import BaseFlasher

class ESPFlasher(BaseFlasher):

    def __init__(self, chip):
        self.chip = chip
        self.process = None  # Store process for cleanup

    def build_command(self, port, package_dir, manifest):
        cmd = [
            "tools/esptool.exe",
            "--chip",
            self.chip,
            "--port",
            port,
            "write-flash"
        ]

        for item in manifest.flash:
            firmware = Path(package_dir) / item.file
            cmd.extend([item.address, str(firmware)])

        return cmd

    def flash(self, port, package_dir, manifest, log_callback=None):
        cmd = self.build_command(port, package_dir, manifest)
        
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
            
            # Wait with timeout
            try:
                self.process.wait(timeout=30)  # 30 second timeout
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
                raise RuntimeError("esptool timed out after 30 seconds")
            
            if self.process.returncode != 0:
                raise RuntimeError(f"esptool exited with code {self.process.returncode}")
                
        finally:
            self.process = None

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(0.5)
            if self.process.poll() is None:
                self.process.kill()