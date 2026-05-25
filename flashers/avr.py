from pathlib import Path
import subprocess
import time
import sys
import platform

from flashers.base import BaseFlasher

class AVRFlasher(BaseFlasher):

    def __init__(self, avrdude_path: str, avrdude_conf: str):
        self.avrdude_path = avrdude_path
        self.avrdude_conf = avrdude_conf
        self.process = None

    def build_command(self, port: str, baud: int, firmware_path: Path, 
                      mcu: str, programmer: str) -> list[str]:
        cmd = [self.avrdude_path]
        
        # Only add -C flag if config file exists
        if self.avrdude_conf and Path(self.avrdude_conf).exists():
            cmd.extend(["-C", self.avrdude_conf])
        
        cmd.extend([
            f"-p{mcu}",
            f"-c{programmer}",
            f"-P{port}",
            f"-b{baud}",
            "-D",
            f"-Uflash:w:{firmware_path}:i",
            "-v"  # Verbose output for debugging
        ])
        
        return cmd

    def _run_command(self, cmd: list[str], log_callback=None) -> bool:
        # Hide console window on Windows
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        # CRITICAL: Set working directory to avrdude's folder
        # This is why manual command works but app doesn't!
        avrdude_dir = str(Path(self.avrdude_path).parent)
        
        if log_callback:
            log_callback(f"Working directory: {avrdude_dir}\n")
        
        # Capture both stdout and stderr
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
            cwd=avrdude_dir  # ← THE FIX
        )
        
        try:
            output_lines = []
            if self.process.stdout:
                while True:
                    ch = self.process.stdout.read(1)
                    if not ch:
                        break
                    
                    output_lines.append(ch)
                    if log_callback:
                        log_callback(ch)
                    else:
                        print(ch, end="", flush=True)
            
            self.process.wait(timeout=60)
            
            output = ''.join(output_lines)
            
            # Check for common errors
            if self.process.returncode != 0:
                if "not in sync" in output.lower():
                    if log_callback:
                        log_callback("\n[ERROR] Device not responding. Check:\n")
                        log_callback("  1. Is the device in bootloader mode?\n")
                        log_callback("  2. Try resetting the device\n")
                        log_callback("  3. Check your connections\n")
                elif "permission denied" in output.lower():
                    if log_callback:
                        log_callback("\n[ERROR] Permission denied. Try:\n")
                        log_callback("  1. Run as administrator\n")
                        log_callback("  2. Check if another program is using the port\n")
                elif "avrdude" in output.lower() and "not found" in output.lower():
                    if log_callback:
                        log_callback(f"\n[ERROR] avrdude not found at: {cmd[0]}\n")
                
                if log_callback:
                    log_callback(f"\navrdude returned code: {self.process.returncode}\n")
            
            return self.process.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
            if log_callback:
                log_callback("\n[ERROR] avrdude timed out after 60 seconds\n")
            return False
        finally:
            self.process = None

    def flash(self, port: str, package_dir, manifest, log_callback=None):
        if not manifest.flash:
            raise RuntimeError("Manifest contains no firmware entries")
        
        # Check if AVR config exists in manifest
        if not manifest.avr:
            raise RuntimeError("Manifest missing AVR configuration (mcu, programmer, baud_rates)")

        # Use the first flash entry (for AVR there's usually just one)
        firmware_path = Path(package_dir) / manifest.flash[0].file

        if not firmware_path.exists():
            raise FileNotFoundError(f"Firmware not found: {firmware_path}")

        # Debug info
        if log_callback:
            log_callback(f"\n=== AVR Debug Info ===\n")
            log_callback(f"avrdude: {self.avrdude_path}\n")
            log_callback(f"avrdude exists: {Path(self.avrdude_path).exists()}\n")
            if self.avrdude_conf:
                log_callback(f"avrdude.conf: {self.avrdude_conf}\n")
                log_callback(f"conf exists: {Path(self.avrdude_conf).exists()}\n")
            log_callback(f"Firmware: {firmware_path}\n")
            log_callback(f"Firmware size: {firmware_path.stat().st_size} bytes\n")
            log_callback(f"=====================\n\n")

        # Use baud rates from manifest
        baud_rates = manifest.avr.baud_rates if manifest.avr.baud_rates else [115200, 57600, 9600]
        
        # Use MCU and programmer from manifest
        mcu = manifest.avr.mcu
        programmer = manifest.avr.programmer

        # Try common reset methods first
        if log_callback:
            log_callback("Note: For Arduino boards, try pressing reset button just before upload\n\n")

        import time
        time.sleep(0.5)  # Short delay before starting upload attempts

        for i, baud in enumerate(baud_rates):
            status_msg = f"[Attempt {i+1}/{len(baud_rates)}] Trying upload at {baud} baud (MCU: {mcu}, Programmer: {programmer})...\n"
            if log_callback:
                log_callback(status_msg)
            else:
                print(status_msg, end="")

            cmd = self.build_command(port, baud, firmware_path, mcu, programmer)
            
            if log_callback:
                log_callback(f"Command: {' '.join(cmd)}\n\n")
            
            success = self._run_command(cmd, log_callback)

            if success:
                success_msg = f"\n✓ Upload successful at {baud} baud!\n"
                if log_callback:
                    log_callback(success_msg)
                else:
                    print(success_msg, end="")
                return

            if log_callback:
                log_callback(f"\n✗ Upload failed at {baud} baud\n\n")

        raise RuntimeError(f"Upload failed using all baud rates: {baud_rates}\n\nTroubleshooting tips:\n"
                          f"1. Verify the device is on port {port}\n"
                          f"2. Check if device is in bootloader mode\n"
                          f"3. Try pressing reset button before upload\n"
                          f"4. Verify MCU '{mcu}' is correct\n"
                          f"5. Verify programmer '{programmer}' is correct")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(0.5)
            if self.process.poll() is None:
                self.process.kill()