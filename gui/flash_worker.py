from PySide6.QtCore import (
    QThread,
    Signal
)


class FlashWorker(QThread):

    log_signal = Signal(str)

    finished_signal = Signal()

    error_signal = Signal(str)

    def __init__(
        self,
        flasher,
        port,
        package_dir,
        manifest
    ):
        super().__init__()

        self.flasher = flasher
        self.port = port
        self.package_dir = package_dir
        self.manifest = manifest

    def run(self):

        try:

            self.flasher.flash(
                self.port,
                self.package_dir,
                self.manifest,
                log_callback=self.log_signal.emit
            )

            self.finished_signal.emit()

        except Exception as e:

            self.error_signal.emit(
                str(e)
            )