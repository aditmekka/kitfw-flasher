import sys
from pathlib import Path

def resource_path(relative_path):

    if hasattr(sys, "_MEIPASS"):
        return str(
            Path(sys._MEIPASS) / relative_path
        )

    return relative_path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QMessageBox,
    QProgressBar,
    QFrame,
    QDialog,
    QHeaderView
)

from PySide6.QtGui import (
    QTextCursor,
    QAction,
    QIcon
)

from PySide6.QtCore import Qt

from core.package_loader import PackageLoader
from core.port_manager import PortManager
from flashers.factory import create_flasher
from gui.flash_worker import FlashWorker


# =====================================================
# Card Widget
# =====================================================

class Card(QFrame):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(
            QIcon("assets/logo.ico")
        )

        self.setObjectName("card")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            16,
            16,
            16,
            16
        )


# =====================================================
# About Dialog
# =====================================================

class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "About KitFW Flasher"
        )

        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        title = QLabel(
            "KitFW Flasher"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size: 22pt;
            font-weight: bold;
            """
        )

        layout.addWidget(title)

        info = QLabel(
            """
            <center>

            Version 0.1

            <br><br>

            Firmware installer for KitFW packages

            <br><br>

            Built and maintained by
            <b>Adit Mekka</b>

            <br><br>

            Copyright © 2026

            <br><br>

            MIT License

            </center>
            """
        )

        info.setWordWrap(True)

        layout.addWidget(info)

        close_btn = QPushButton(
            "Close"
        )

        close_btn.clicked.connect(
            self.accept
        )

        layout.addWidget(close_btn)


# =====================================================
# Main Window
# =====================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.package_dir = None
        self.manifest = None

        self.setWindowTitle(
            "KitFW Flasher"
        )

        self.resize(
            1200,
            850
        )

        self.build_ui()

        self.refresh_ports()

        self.set_status(
            "READY"
        )

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        #
        # Central widget
        #

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setSpacing(16)

        #
        # Menu
        #

        file_menu = self.menuBar().addMenu(
            "File"
        )

        help_menu = self.menuBar().addMenu(
            "Help"
        )

        about_action = QAction(
            "About",
            self
        )

        about_action.triggered.connect(
            self.show_about
        )

        help_menu.addAction(
            about_action
        )

        #
        # Header
        #

        header_row = QHBoxLayout()

        title_column = QVBoxLayout()

        title = QLabel(
            "KitFW Flasher"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "Install firmware packages in one click"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_column.addWidget(
            title
        )

        title_column.addWidget(
            subtitle
        )

        self.status_badge = QLabel()

        header_row.addLayout(
            title_column
        )

        header_row.addStretch()

        header_row.addWidget(
            self.status_badge
        )

        main_layout.addLayout(
            header_row
        )

        #
        # Top Cards
        #

        top_row = QHBoxLayout()

        #
        # Package Card
        #

        package_card = Card()

        package_title = QLabel(
            "📦 Firmware Package"
        )

        package_title.setStyleSheet(
            "font-weight:bold;"
        )

        self.open_button = QPushButton(
            "Open .kitfw Package"
        )

        self.open_button.clicked.connect(
            self.open_package
        )

        self.package_name = QLabel(
            "No Package Loaded"
        )

        self.package_name.setStyleSheet(
            """
            font-size:16pt;
            font-weight:bold;
            """
        )

        self.package_meta = QLabel(
            "Open a package to begin"
        )

        package_card.layout.addWidget(
            package_title
        )

        package_card.layout.addWidget(
            self.open_button
        )

        package_card.layout.addWidget(
            self.package_name
        )

        package_card.layout.addWidget(
            self.package_meta
        )

        #
        # Device Card
        #

        device_card = Card()

        device_title = QLabel(
            "🔌 Connected Device"
        )

        device_title.setStyleSheet(
            "font-weight:bold;"
        )

        self.port_combo = QComboBox()

        refresh_btn = QPushButton(
            "Refresh"
        )

        refresh_btn.clicked.connect(
            self.refresh_ports
        )

        device_card.layout.addWidget(
            device_title
        )

        device_card.layout.addWidget(
            self.port_combo
        )

        device_card.layout.addWidget(
            refresh_btn
        )

        top_row.addWidget(
            package_card,
            1
        )

        top_row.addWidget(
            device_card,
            1
        )

        main_layout.addLayout(
            top_row
        )

        #
        # Contents Card
        #

        contents_card = Card()

        contents_title = QLabel(
            "📁 Package Contents"
        )

        contents_title.setStyleSheet(
            "font-weight:bold;"
        )

        self.contents_table = QTableWidget()

        self.contents_table.setColumnCount(
            2
        )

        self.contents_table.setHorizontalHeaderLabels(
            [
                "Address",
                "File"
            ]
        )

        self.contents_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        contents_card.layout.addWidget(
            contents_title
        )

        contents_card.layout.addWidget(
            self.contents_table
        )

        main_layout.addWidget(
            contents_card
        )

        #
        # Buttons
        #

        button_row = QHBoxLayout()

        self.flash_button = QPushButton(
            "⚡ FLASH DEVICE"
        )

        self.flash_button.setObjectName(
            "flashButton"
        )

        self.flash_button.setEnabled(
            False
        )

        self.flash_button.clicked.connect(
            self.flash_firmware
        )

        self.stop_button = QPushButton(
            "⛔ STOP FLASH"
        )

        self.stop_button.setObjectName(
            "stopButton"
        )

        self.stop_button.setEnabled(
            False
        )

        self.stop_button.clicked.connect(
            self.stop_flash
        )

        button_row.addWidget(
            self.flash_button
        )

        button_row.addWidget(
            self.stop_button
        )

        main_layout.addLayout(
            button_row
        )

        #
        # Progress
        #

        self.progress = QProgressBar()

        self.progress.setValue(0)

        main_layout.addWidget(
            self.progress
        )

        #
        # Logs Card
        #

        logs_card = Card()

        logs_title = QLabel(
            "📜 Live Flash Log"
        )

        logs_title.setStyleSheet(
            "font-weight:bold;"
        )

        self.logs = QPlainTextEdit()

        self.logs.setReadOnly(
            True
        )

        logs_card.layout.addWidget(
            logs_title
        )

        logs_card.layout.addWidget(
            self.logs
        )

        main_layout.addWidget(
            logs_card,
            1
        )

    # =====================================================
    # Status Badge
    # =====================================================

    def set_status(self, state):

        if state == "READY":

            self.status_badge.setText(
                "● READY"
            )

            self.status_badge.setObjectName(
                "badge_ready"
            )

        elif state == "FLASHING":

            self.status_badge.setText(
                "● FLASHING"
            )

            self.status_badge.setObjectName(
                "badge_flashing"
            )

        elif state == "SUCCESS":

            self.status_badge.setText(
                "● SUCCESS"
            )

            self.status_badge.setObjectName(
                "badge_success"
            )

        elif state == "ERROR":

            self.status_badge.setText(
                "● ERROR"
            )

            self.status_badge.setObjectName(
                "badge_error"
            )

        self.style().unpolish(
            self.status_badge
        )

        self.style().polish(
            self.status_badge
        )

    # =====================================================
    # About
    # =====================================================

    def show_about(self):

        dialog = AboutDialog(self)

        dialog.exec()

    # =====================================================
    # Package Loading
    # =====================================================

    def open_package(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open KitFW Package",
            "",
            "KitFW Files (*.kitfw)"
        )

        if not file_name:
            return

        try:

            loader = PackageLoader()

            self.package_dir, self.manifest = (
                loader.load(file_name)
            )

            self.package_name.setText(
                self.manifest.name
            )

            self.package_meta.setText(
                (
                    f"Version {self.manifest.version}\n"
                    f"Target: {self.manifest.target.upper()}"
                )
            )

            self.populate_table()

            self.flash_button.setEnabled(
                True
            )

            self.append_log(
                f"\nLoaded package:\n{file_name}\n"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Package Error",
                str(e)
            )

    # =====================================================
    # Contents Table
    # =====================================================

    def populate_table(self):

        self.contents_table.clearContents()

        self.contents_table.setRowCount(
            len(self.manifest.flash)
        )

        for row, entry in enumerate(
            self.manifest.flash
        ):

            address = ""

            if entry.address:
                address = entry.address

            self.contents_table.setItem(
                row,
                0,
                QTableWidgetItem(address)
            )

            self.contents_table.setItem(
                row,
                1,
                QTableWidgetItem(entry.file)
            )

    # =====================================================
    # COM Refresh
    # =====================================================

    def refresh_ports(self):

        current = self.port_combo.currentText()

        self.port_combo.clear()

        ports = PortManager.list_ports()

        for port in ports:

            self.port_combo.addItem(
                port["description"],
                port["device"]
            )

        index = self.port_combo.findText(
            current
        )

        if index >= 0:

            self.port_combo.setCurrentIndex(
                index
            )

    # =====================================================
    # Logging
    # =====================================================

    def append_log(self, text):

        self.logs.moveCursor(
            QTextCursor.MoveOperation.End
        )

        self.logs.insertPlainText(
            text
        )

        self.logs.ensureCursorVisible()

    # =====================================================
    # Flash Firmware
    # =====================================================

    def flash_firmware(self):

        if self.manifest is None:

            QMessageBox.warning(
                self,
                "No Package",
                "Load a package first."
            )

            return

        port = self.port_combo.currentData()

        if not port:

            QMessageBox.warning(
                self,
                "No Port",
                "Select a COM port."
            )

            return

        self.logs.clear()

        self.append_log(
            "=====================================\n"
        )

        self.append_log(
            "KitFW Flash Session\n"
        )

        self.append_log(
            "=====================================\n\n"
        )

        self.append_log(
            f"Target : {self.manifest.target}\n"
        )

        self.append_log(
            f"Port   : {port}\n\n"
        )

        self.progress.setRange(
            0,
            0
        )

        self.set_status(
            "FLASHING"
        )

        self.flash_button.setEnabled(
            False
        )

        self.stop_button.setEnabled(
            True
        )

        self.flasher = create_flasher(
            self.manifest.target
        )

        self.worker = FlashWorker(
            self.flasher,
            port,
            self.package_dir,
            self.manifest
        )

        self.worker.log_signal.connect(
            self.append_log
        )

        self.worker.finished_signal.connect(
            self.flash_finished
        )

        self.worker.error_signal.connect(
            self.flash_error
        )

        self.worker.start()

    # =====================================================
    # Flash Success
    # =====================================================

    def flash_finished(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            100
        )

        self.flash_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.set_status(
            "SUCCESS"
        )

        self.append_log(
            "\n\nFlash completed successfully.\n"
        )

        QMessageBox.information(
            self,
            "Success",
            "Firmware flashed successfully."
        )

    # =====================================================
    # Flash Error
    # =====================================================

    def flash_error(self, error):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        self.flash_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.set_status(
            "ERROR"
        )

        self.append_log(
            f"\n\nERROR:\n{error}\n"
        )

        QMessageBox.critical(
            self,
            "Flash Failed",
            error
        )

    # =====================================================
    # Stop Flash
    # =====================================================

    def stop_flash(self):

        if hasattr(self, "flasher"):

            self.append_log(
                "\n\nStopping flash...\n"
            )

            try:

                self.flasher.stop()

            except Exception as e:

                self.append_log(
                    f"\nStop error:\n{e}\n"
                )

        self.flash_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        self.set_status(
            "READY"
        )