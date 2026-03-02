"""PyQt6 GUI frontend for Vibe Translating.

Provides a desktop application with VS Code-like layout
for translation tasks.
"""

import sys
from typing import Any, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ...backend.service import BackendService
from ..common.protocol import Request


class TranslateWorker(QThread):
    """Background worker for translation tasks."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self, service: BackendService, text: str
    ) -> None:
        """Initialize worker.

        Args:
            service: Backend service.
            text: Text to translate.
        """
        super().__init__()
        self.service = service
        self.text = text

    def run(self) -> None:
        """Execute translation in background."""
        try:
            response = self.service.handle_request(
                Request(
                    method="translate",
                    params={"text": self.text},
                )
            )
            if response.success:
                self.finished.emit(response.data)
            else:
                self.error.emit(response.error or "Unknown error")
        except Exception as e:
            self.error.emit(str(e))


class ActivityBar(QWidget):
    """VS Code-like activity bar with icon buttons."""

    mode_changed = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize activity bar."""
        super().__init__()
        self.setFixedWidth(48)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)

        self._buttons: dict[str, QToolButton] = {}
        modes = [
            ("realtime", "🔄"),
            ("book", "📚"),
            ("frame_select", "🖼️"),
            ("supervision", "📝"),
            ("settings", "⚙️"),
            ("plugins", "🧩"),
        ]
        for name, icon in modes:
            btn = QToolButton()
            btn.setText(icon)
            btn.setFixedSize(48, 48)
            btn.setCheckable(True)
            btn.setFont(QFont("", 18))
            btn.setStyleSheet(
                "QToolButton { border: none; "
                "border-left: 2px solid transparent; }"
                "QToolButton:checked { "
                "border-left: 2px solid #007acc; }"
                "QToolButton:hover { background: #2a2d2e; }"
            )
            btn.clicked.connect(
                lambda checked, m=name: self._on_click(m)
            )
            layout.addWidget(btn)
            self._buttons[name] = btn

        layout.addStretch()
        self._buttons["realtime"].setChecked(True)

    def _on_click(self, mode: str) -> None:
        """Handle button click."""
        for name, btn in self._buttons.items():
            btn.setChecked(name == mode)
        self.mode_changed.emit(mode)


class SideBar(QWidget):
    """Sidebar with terms, bookmarks, and memory info."""

    def __init__(self, service: BackendService) -> None:
        """Initialize sidebar."""
        super().__init__()
        self.service = service
        self.setFixedWidth(250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("  EXPLORER")
        title.setFixedHeight(30)
        title.setStyleSheet(
            "font-size: 11px; color: #969696; "
            "text-transform: uppercase; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        terms_group = QGroupBox("Terms")
        terms_layout = QVBoxLayout(terms_group)
        self.terms_list = QListWidget()
        self.terms_list.setMaximumHeight(150)
        terms_layout.addWidget(self.terms_list)
        layout.addWidget(terms_group)

        bm_group = QGroupBox("Bookmarks")
        bm_layout = QVBoxLayout(bm_group)
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setMaximumHeight(120)
        bm_layout.addWidget(self.bookmarks_list)
        layout.addWidget(bm_group)

        mem_group = QGroupBox("Memory")
        mem_layout = QVBoxLayout(mem_group)
        self.memory_label = QLabel("No data")
        self.memory_label.setWordWrap(True)
        mem_layout.addWidget(self.memory_label)
        layout.addWidget(mem_group)

        layout.addStretch()

    def refresh(self) -> None:
        """Refresh sidebar data from backend."""
        resp = self.service.handle_request(
            Request(method="get_memory")
        )
        if not resp.success:
            return
        data = resp.data
        self.terms_list.clear()
        for t in data.get("terms", []):
            self.terms_list.addItem(
                f"{t['source']} → {t['target']}"
            )
        self.bookmarks_list.clear()
        for b in data.get("bookmarks", []):
            self.bookmarks_list.addItem(
                f"[{b['position']}] {b.get('label', '')}"
            )
        terms_count = len(data.get("terms", []))
        notes_count = len(data.get("notes", []))
        self.memory_label.setText(
            f"Terms: {terms_count}, Notes: {notes_count}"
        )


class RealtimePanel(QWidget):
    """Realtime translation panel."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        self.service = service
        self._worker: Optional[TranslateWorker] = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Source Text:"))
        self.source_input = QPlainTextEdit()
        self.source_input.setPlaceholderText(
            "Enter text to translate..."
        )
        self.source_input.setMaximumHeight(160)
        layout.addWidget(self.source_input)

        btn_layout = QHBoxLayout()
        self.translate_btn = QPushButton("Translate")
        self.translate_btn.setStyleSheet(
            "background: #007acc; color: white; "
            "padding: 8px 20px; border: none; border-radius: 4px;"
        )
        self.translate_btn.clicked.connect(self._translate)
        btn_layout.addWidget(self.translate_btn)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Translation Only", "Side by Side",
        ])
        btn_layout.addWidget(self.mode_combo)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("Translation:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText(
            "Translation will appear here..."
        )
        layout.addWidget(self.result_display)

    def _translate(self) -> None:
        """Start translation."""
        text = self.source_input.toPlainText().strip()
        if not text:
            return
        self.translate_btn.setEnabled(False)
        self.result_display.setPlainText("Translating...")
        self._worker = TranslateWorker(self.service, text)
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, data: dict) -> None:
        """Handle translation result."""
        self.translate_btn.setEnabled(True)
        self.result_display.setPlainText(
            data.get("translation", "")
        )

    def _on_error(self, error: str) -> None:
        """Handle translation error."""
        self.translate_btn.setEnabled(True)
        self.result_display.setPlainText(f"Error: {error}")


class BookPanel(QWidget):
    """Book translation panel."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        self.service = service
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Book Content:"))
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(
            "Paste book content here..."
        )
        layout.addWidget(self.text_input)

        self.process_btn = QPushButton("Process Book")
        self.process_btn.clicked.connect(self._process)
        layout.addWidget(self.process_btn)

        self.chapters_list = QListWidget()
        layout.addWidget(self.chapters_list)

    def _process(self) -> None:
        """Process book content."""
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        resp = self.service.handle_request(
            Request(
                method="process_content",
                params={"mode": "book", "content": text},
            )
        )
        self.chapters_list.clear()
        if resp.success and resp.data.get("chapters"):
            for ch in resp.data["chapters"]:
                self.chapters_list.addItem(
                    f"{ch['title']}: "
                    f"{ch['content'][:60]}..."
                )


class FrameSelectPanel(QWidget):
    """Frame select translation panel."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Frame Select Mode"))
        placeholder = QLabel(
            "Drop an image here or click to upload"
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setMinimumHeight(300)
        placeholder.setStyleSheet(
            "border: 1px dashed #3e3e3e; "
            "border-radius: 4px; color: #969696;"
        )
        layout.addWidget(placeholder)


class SupervisionPanel(QWidget):
    """Supervision mode panel."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        self.service = service
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Source Text:"))
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(
            "Paste source text..."
        )
        self.text_input.setMaximumHeight(150)
        layout.addWidget(self.text_input)

        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self._process)
        layout.addWidget(self.process_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.source_list = QListWidget()
        self.target_list = QListWidget()
        splitter.addWidget(self.source_list)
        splitter.addWidget(self.target_list)
        layout.addWidget(splitter)

    def _process(self) -> None:
        """Process supervision content."""
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        resp = self.service.handle_request(
            Request(
                method="process_content",
                params={
                    "mode": "supervision",
                    "content": text,
                },
            )
        )
        self.source_list.clear()
        self.target_list.clear()
        if resp.success and resp.data.get("pairs"):
            for p in resp.data["pairs"]:
                self.source_list.addItem(p["source"])
                self.target_list.addItem(
                    p["target"] or "(pending)"
                )


class SettingsPanel(QWidget):
    """Settings panel with GUI controls for all config."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        self.service = service
        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form = QFormLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save)
        main_layout.addWidget(save_btn)

        self._controls: dict[str, QWidget] = {}
        self._build_settings()

    def _build_settings(self) -> None:
        """Build settings form from config."""
        config = self.service.config.get_flat()
        enums = {
            "api.provider": ["openai", "ollama"],
            "translation.mode": [
                "realtime", "book", "frame_select",
                "supervision",
            ],
            "translation.source_language": [
                "ja", "en", "ko", "fr", "de", "es", "zh-CN",
            ],
            "translation.target_language": [
                "zh-CN", "en", "ja", "ko", "fr", "de", "es",
            ],
            "frontend.type": ["cli", "webui", "gui"],
            "app.theme": ["light", "dark"],
            "app.language": ["en", "zh-CN", "ja"],
        }
        for key, value in sorted(config.items()):
            if isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                widget.stateChanged.connect(
                    lambda s, k=key: self._on_change(
                        k, s == Qt.CheckState.Checked.value
                    )
                )
            elif key in enums:
                widget = QComboBox()
                widget.addItems(enums[key])
                idx = widget.findText(str(value))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
                widget.currentTextChanged.connect(
                    lambda v, k=key: self._on_change(k, v)
                )
            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setRange(0.0, 10.0)
                widget.setSingleStep(0.05)
                widget.setValue(value)
                widget.valueChanged.connect(
                    lambda v, k=key: self._on_change(k, v)
                )
            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setRange(0, 100000)
                widget.setValue(value)
                widget.valueChanged.connect(
                    lambda v, k=key: self._on_change(k, v)
                )
            elif isinstance(value, list):
                widget = QLineEdit()
                import json
                widget.setText(json.dumps(value))
                widget.editingFinished.connect(
                    lambda w=widget, k=key: self._on_list_change(
                        k, w
                    )
                )
            else:
                widget = QLineEdit()
                widget.setText(str(value))
                widget.editingFinished.connect(
                    lambda w=widget, k=key: self._on_change(
                        k, w.text()
                    )
                )
            self._controls[key] = widget
            self.form.addRow(key, widget)

    def _on_change(self, key: str, value: Any) -> None:
        """Handle config value change."""
        self.service.handle_request(
            Request(
                method="set_config",
                params={"key": key, "value": value},
            )
        )

    def _on_list_change(
        self, key: str, widget: QLineEdit
    ) -> None:
        """Handle list config change."""
        import json
        try:
            value = json.loads(widget.text())
            self._on_change(key, value)
        except json.JSONDecodeError:
            pass

    def _save(self) -> None:
        """Save configuration."""
        self.service.handle_request(
            Request(method="save_config")
        )


class PluginsPanel(QWidget):
    """Plugins panel."""

    def __init__(self, service: BackendService) -> None:
        """Initialize panel."""
        super().__init__()
        self.service = service
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Plugins"))
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)

        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load plugin information."""
        resp = self.service.handle_request(
            Request(method="get_plugins")
        )
        self.plugin_list.clear()
        if resp.success:
            for name, info in resp.data.items():
                status = "✓" if info["active"] else "✗"
                self.plugin_list.addItem(
                    f"{status} {name} v{info['version']} - "
                    f"{info['description']}"
                )


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.service = BackendService()
        self.setWindowTitle("Vibe Translating")
        self.resize(
            self.service.config.get(
                "frontend.gui.window_width", 1200
            ),
            self.service.config.get(
                "frontend.gui.window_height", 800
            ),
        )
        self._setup_theme()
        self._setup_ui()
        self._check_api()

    def _setup_theme(self) -> None:
        """Apply dark theme."""
        palette = QPalette()
        palette.setColor(
            QPalette.ColorRole.Window, QColor("#1e1e1e")
        )
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor("#cccccc")
        )
        palette.setColor(
            QPalette.ColorRole.Base, QColor("#252526")
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase,
            QColor("#2d2d2d"),
        )
        palette.setColor(
            QPalette.ColorRole.Text, QColor("#cccccc")
        )
        palette.setColor(
            QPalette.ColorRole.Button, QColor("#2d2d2d")
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText, QColor("#cccccc")
        )
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor("#007acc")
        )
        QApplication.instance().setPalette(palette)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.activity_bar = ActivityBar()
        self.activity_bar.mode_changed.connect(
            self._on_mode_changed
        )
        main_layout.addWidget(self.activity_bar)

        self.sidebar = SideBar(self.service)
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.panels = {
            "realtime": RealtimePanel(self.service),
            "book": BookPanel(self.service),
            "frame_select": FrameSelectPanel(self.service),
            "supervision": SupervisionPanel(self.service),
            "settings": SettingsPanel(self.service),
            "plugins": PluginsPanel(self.service),
        }
        for panel in self.panels.values():
            self.stack.addWidget(panel)
        main_layout.addWidget(self.stack)

        self.statusBar().showMessage("Ready")

    def _on_mode_changed(self, mode: str) -> None:
        """Handle mode change from activity bar."""
        panel = self.panels.get(mode)
        if panel:
            self.stack.setCurrentWidget(panel)
            self.sidebar.refresh()

    def _check_api(self) -> None:
        """Check API availability."""
        resp = self.service.handle_request(
            Request(method="check_api")
        )
        if resp.success:
            data = resp.data
            status = (
                "Connected" if data["available"]
                else "Unavailable"
            )
            self.statusBar().showMessage(
                f"{data['provider']}: {status}"
            )


def main() -> None:
    """Entry point for GUI frontend."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
