from .base import *

from gui.model_session import SessionTableModel
from gui.add_session_dialog import AddSessionDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBVigil Session 管理")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.table = QTableView(self)
        self.model = SessionTableModel()
        self.table.setModel(self.model)
        from PySide6.QtWidgets import QAbstractItemView

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(self.open_session_window)

        layout.addWidget(self.table)
        self.setCentralWidget(central_widget)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, pos):
        menu = QMenu(self)
        add_action = QAction("添加", self)
        del_action = QAction("删除", self)
        menu.addAction(add_action)
        menu.addAction(del_action)
        add_action.triggered.connect(self.add_session)
        del_action.triggered.connect(self.delete_session)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def add_session(self):

        dialog = AddSessionDialog(self)
        result = dialog.exec()
        if result == QDialog.Accepted:
            session = dialog.get_data()
            if not session["host"] or not session["user"]:
                QMessageBox.warning(self, "提示", "Host 和 User 不能为空")
                return
            self.model.add_session(session)
        else:
            QMessageBox.information(self, "提示", "添加 Session 已取消")
            return

    def delete_session(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            QMessageBox.warning(self, "提示", "请先选中要删除的 Session")
            return
        self.model.remove_session(idx.row())

    def open_session_window(self, index):
        session = self.model.sessions[index.row()]
        from gui.session_interaction import SessionInteractionWidget

        self.session_window = SessionInteractionWidget(session)
        self.session_window.setWindowTitle(f"Session: {session['host']}@{session['user']}")
        self.session_window.resize(600, 400)
        self.session_window.show()
