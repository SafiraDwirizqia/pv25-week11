import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from F1D022096_main import ManajemenBuku

class ManajemenBukuExtended(ManajemenBuku):
    def __init__(self):
        super().__init__()

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.statusBar().showMessage("Safira Dwirizqia - F1D022096")

        self.addDockWidgetInfo()
        self.addFormInputDock()

    def addFormInputDock(self):
        self.formDock = QDockWidget("📥 Form Input Buku", self)
        self.formDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        formWidget = QWidget()
        layout = QFormLayout()

        layout.addRow("Judul:", self.judulInput)
        self.judulInputLayout = layout
        layout.addRow("Pengarang:", self.pengarangInput)
        layout.addRow("Tahun:", self.tahunInput)
        layout.addRow(self.tambahButton)

        formWidget.setLayout(layout)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(formWidget)

        self.formDock.setWidget(scrollArea)
        self.formDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.formDock)

        self.addClipboardButton()

    def addClipboardButton(self):
        clipboardBtn = QPushButton("📋 Tempel dari Clipboard")
        clipboardBtn.setToolTip("Tempel teks dari clipboard ke input Judul")
        clipboardBtn.setStyleSheet("padding: 5px; background-color: #4CAF50; color: black;")
        clipboardBtn.clicked.connect(self.pasteFromClipboard)

        self.judulInputLayout.addRow("", clipboardBtn)

    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            self.judulInput.setText(clipboard_text)
        else:
            QMessageBox.information(self, "Clipboard Kosong", "Tidak ada teks di clipboard.")

    def addDockWidgetInfo(self):
        self.infoDock = QDockWidget("ℹ️ Info Aplikasi", self)
        self.infoDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        infoWidget = QTextEdit()
        infoWidget.setReadOnly(True)
        infoWidget.setText(
            "📚 Aplikasi Manajemen Buku\n\n"
            "- Tambah data buku ke database\n"
            "- Klik dua kali data untuk mengedit\n"
            "- Gunakan pencarian judul\n"
            "- Ekspor data ke CSV\n"
            "- Gunakan clipboard untuk paste teks"
        )

        self.infoDock.setWidget(infoWidget)
        self.infoDock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.RightDockWidgetArea, self.infoDock)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManajemenBukuExtended()
    window.show()
    sys.exit(app.exec_())
