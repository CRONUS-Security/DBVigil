from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QMenu, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint

class SessionListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.session_list = QListWidget(self)
        self.layout.addWidget(self.session_list)
        self.add_btn = QPushButton("添加 Session", self)
        self.layout.addWidget(self.add_btn)
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.open_menu)
        self.add_btn.clicked.connect(self.add_session)

    def open_menu(self, pos: QPoint):
        item = self.session_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        edit_action = QAction("编辑", self)
        delete_action = QAction("删除", self)
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        edit_action.triggered.connect(lambda: self.edit_session(item))
        delete_action.triggered.connect(lambda: self.delete_session(item))
        menu.exec(self.session_list.mapToGlobal(pos))

    def add_session(self):
        # TODO: 打开添加 session 的对话框
        QMessageBox.information(self, "添加 Session", "这里弹出添加 Session 的对话框")

    def edit_session(self, item):
        # TODO: 打开编辑 session 的对话框
        QMessageBox.information(self, "编辑 Session", f"编辑: {item.text()}")

    def delete_session(self, item):
        row = self.session_list.row(item)
        self.session_list.takeItem(row)
        QMessageBox.information(self, "删除 Session", f"已删除: {item.text()}")
