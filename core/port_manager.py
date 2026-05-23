from serial.tools import list_ports

class PortManager:
    
    @staticmethod
    def list_ports():
        return [
            {
                "device": p.device,
                "description": p.description
            }
            for p in list_ports.comports()
        ]