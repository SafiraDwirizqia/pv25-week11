import sys
import sqlite3
import csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class ManajemenBuku(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1D022096 - Manajemen Buku")
        self.setGeometry(100, 100, 1517, 1000)

        self.conn = sqlite3.connect("booksdb.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("PRAGMA table_info(book)")
        columns = self.cursor.fetchall()
        if not columns:
            QMessageBox.critical(self, "Error", "Tabel 'book' tidak ditemukan dalam database!")
            sys.exit(1)

        self.initUI()
        self.loadData()

    def initUI(self):
        self.createMenuBar()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab Data Buku
        self.dataBukuTab = QWidget()
        self.initDataBukuTab()
        self.tabs.addTab(self.dataBukuTab, "Data Buku")

        # Tab Ekspor
        self.exportTab = QWidget()
        self.tabs.addTab(self.exportTab, "Ekspor")

        self.tabs.currentChanged.connect(self.handleTabChange)

    def createMenuBar(self):
        menubar = self.menuBar()

        # Menu File
        fileMenu = menubar.addMenu("File")

        saveAction = QAction("Simpan", self)
        saveAction.triggered.connect(self.saveData)
        fileMenu.addAction(saveAction)

        exportAction = QAction("Ekspor ke CSV", self)
        exportAction.triggered.connect(self.performExport)
        fileMenu.addAction(exportAction)

        exitAction = QAction("Keluar", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # Menu Edit
        editMenu = menubar.addMenu("Edit")

        searchAction = QAction("Cari Judul", self)
        searchAction.triggered.connect(self.focusCariJudul)
        editMenu.addAction(searchAction)

        deleteAction = QAction("Hapus Data", self)
        deleteAction.triggered.connect(self.hapusData)
        editMenu.addAction(deleteAction)

        # Submenu AutoFill
        autoFillMenu = editMenu.addMenu("AutoFill")

        judulFillAction = QAction("Judul", self)
        judulFillAction.triggered.connect(lambda: self.autoFill("judul"))
        autoFillMenu.addAction(judulFillAction)

        pengarangFillAction = QAction("Pengarang", self)
        pengarangFillAction.triggered.connect(lambda: self.autoFill("pengarang"))
        autoFillMenu.addAction(pengarangFillAction)

        tahunFillAction = QAction("Tahun", self)
        tahunFillAction.triggered.connect(lambda: self.autoFill("tahun"))
        autoFillMenu.addAction(tahunFillAction)

        startDictationAction = QAction("Start dictation", self)
        startDictationAction.triggered.connect(self.startDictation)
        editMenu.addAction(startDictationAction)

        emojiAction = QAction("Emoji & Symbols", self)
        emojiAction.triggered.connect(self.showEmojiSymbols)
        editMenu.addAction(emojiAction)

    def initDataBukuTab(self):
        layout = QVBoxLayout()

        # Form input
        formLayout = QHBoxLayout()
        self.judulInput = QLineEdit()
        self.pengarangInput = QLineEdit()
        self.tahunInput = QLineEdit()

        self.tambahButton = QPushButton("Simpan")
        self.tambahButton.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px 10px;")
        self.tambahButton.clicked.connect(self.tambahBuku)

        # Search
        searchLayout = QHBoxLayout()
        self.cariJudulInput = QLineEdit()
        self.cariJudulInput.setPlaceholderText("cari judul...")
        self.cariJudulInput.textChanged.connect(self.cariJudul)
        searchLayout.addWidget(self.cariJudulInput)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.editData)

        self.hapusButton = QPushButton("Hapus Data")
        self.hapusButton.setStyleSheet("background-color: orange; color: white; font-weight: bold; padding: 5px 10px;")
        self.hapusButton.clicked.connect(self.hapusData)

        layout.addLayout(formLayout)
        layout.addWidget(self.tambahButton)
        layout.addLayout(searchLayout)
        layout.addWidget(self.table)
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.hapusButton)
        self.tambahButton.setFixedSize(250, 50)
        self.hapusButton.setFixedSize(250, 50)

        layout.addLayout(bottomLayout)

        self.dataBukuTab.setLayout(layout)

    def loadData(self, filter_judul=""):
        self.table.setRowCount(0)
        if filter_judul:
            query = "SELECT id, judul, penulis, tahun FROM book WHERE judul LIKE ?"
            self.cursor.execute(query, (f"%{filter_judul}%",))
        else:
            self.cursor.execute("SELECT id, judul, penulis, tahun FROM book")
        for row_number, row_data in enumerate(self.cursor.fetchall()):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if column_number == 0:
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_number, column_number, item)

    def tambahBuku(self):
        judul = self.judulInput.text()
        pengarang = self.pengarangInput.text()
        tahun = self.tahunInput.text()

        if not (judul and pengarang and tahun.isdigit()):
            QMessageBox.warning(self, "Peringatan", "Harap isi semua kolom dengan benar.")
            return

        self.cursor.execute("INSERT INTO book (judul, penulis, tahun) VALUES (?, ?, ?)",
                            (judul, pengarang, int(tahun)))
        self.conn.commit()
        self.loadData()
        self.judulInput.clear()
        self.pengarangInput.clear()
        self.tahunInput.clear()

    def hapusData(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang ingin dihapus.")
            return

        id_item = self.table.item(selected, 0)
        if id_item:
            id_buku = int(id_item.text())
            reply = QMessageBox.question(self, 'Konfirmasi',
                                         f'Hapus buku ID {id_buku}?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM book WHERE id = ?", (id_buku,))
                self.conn.commit()
                self.loadData()

    def editData(self, row, column):
        if column in [1, 2, 3]:
            current_value = self.table.item(row, column).text()
            column_names = ["", "judul", "penulis", "tahun"]
            display_names = ["", "Judul", "Pengarang", "Tahun"]

            if column == 3:
                new_value, ok = QInputDialog.getText(self, f"Edit {display_names[column]}",
                                                     f"{display_names[column]}:",
                                                     text=current_value)
                if ok and new_value.strip() and new_value.isdigit():
                    id_buku = int(self.table.item(row, 0).text())
                    self.cursor.execute(f"UPDATE book SET {column_names[column]} = ? WHERE id = ?",
                                        (int(new_value), id_buku))
                    self.conn.commit()
                    self.loadData()
            else:
                new_value, ok = QInputDialog.getText(self, f"Edit {display_names[column]}",
                                                     f"{display_names[column]}:",
                                                     text=current_value)
                if ok and new_value.strip():
                    id_buku = int(self.table.item(row, 0).text())
                    self.cursor.execute(f"UPDATE book SET {column_names[column]} = ? WHERE id = ?",
                                        (new_value, id_buku))
                    self.conn.commit()
                    self.loadData()

    def editSelectedRow(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin diedit.")
            return
        self.editData(row, 1)

    def cariJudul(self):
        keyword = self.cariJudulInput.text()
        self.loadData(filter_judul=keyword)

    def performExport(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not save_path:
            return

        try:
            with open(save_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                self.cursor.execute("SELECT id, judul, penulis, tahun FROM book")
                for row in self.cursor.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Berhasil", "Data berhasil diekspor!")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", "Terjadi kesalahan saat mengekspor!")

    def handleTabChange(self, index):
        if self.tabs.tabText(index) == "Ekspor":
            self.performExport()
            self.tabs.setCurrentWidget(self.dataBukuTab)

    def saveData(self):
        QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dipilih!")

    def focusCariJudul(self):
        self.cariJudulInput.setFocus()

    def autoFill(self, field):
        if field == "judul":
            QMessageBox.information(self, "autoFill", "Fitur autoFill judul belum diimplementasikan.")
        elif field == "pengarang":
            QMessageBox.information(self, "autoFill", "Fitur autoFill pengarang belum diimplementasikan.")
        elif field == "tahun":
            QMessageBox.information(self, "autoFill", "Fitur autoFill tahun belum diimplementasikan.")

    def startDictation(self):
        QMessageBox.information(self, "Start dictation", "Fitur Start dictation belum diimplementasikan.")

    def showEmojiSymbols(self):
        QMessageBox.information(self, "Emoji & Symbols", "Fitur Emoji & Symbols belum diimplementasikan.")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManajemenBuku()
    window.show()
    sys.exit(app.exec_())
