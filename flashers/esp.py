from pathlib import Path
import subprocess
import time
import sys
import platform

from flashers.base import BaseFlasher

class ESPFlasher(BaseFlasher):

    def __init__(self, chip):
        self.chip = chip
        self.process = None
        
        # Get correct path to esptool
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent
        
        self.esptool_path = str(base_path / "tools" / "esptool.exe")
        
        # Verify esptool exists
        if not Path(self.esptool_path).exists():
            import shutil
            system_esptool = shutil.which("esptool") or shutil.which("esptool.exe")
            if system_esptool:
                self.esptool_path = system_esptool

    def build_command(self, port, package_dir, manifest):
        cmd = [
            self.esptool_path,
            "--chip", self.chip,
            "--port", port,
            "write-flash"
        ]

        # Add flash parameters from manifest if available
        if hasattr(manifest, 'esp') and manifest.esp:
            if 'flash_mode' in manifest.esp:
                cmd.extend(["--flash-mode", manifest.esp['flash_mode']])
            if 'flash_size' in manifest.esp:
                cmd.extend(["--flash-size", manifest.esp['flash_size']])
            if 'flash_freq' in manifest.esp:
                cmd.extend(["--flash-freq", manifest.esp['flash_freq']])

        for item in manifest.flash:
            firmware = Path(package_dir) / item.file
            cmd.extend([item.address, str(firmware)])

        return cmd

    def flash(self, port, package_dir, manifest, log_callback=None):
        cmd = self.build_command(port, package_dir, manifest)
        
        if log_callback:
            log_callback(f"Using esptool: {self.esptool_path}\n")
            log_callback(f"Command: {' '.join(cmd)}\n\n")
        
        # Hide console window on Windows
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            startupinfo=startupinfo,  # Hide window
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
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
            
            try:
                self.process.wait(timeout=30)
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