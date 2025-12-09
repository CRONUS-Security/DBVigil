from .base import *

class SessionInteractionWidget(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.layout = QVBoxLayout(self)
        self.info_label = QLabel(f"连接信息: host={session['host']}, user={session['user']}, type={session['type']}, add_time={session['add_time']}", self)
        self.layout.addWidget(self.info_label)
        self.query_edit = QTextEdit(self)
        self.layout.addWidget(self.query_edit)
        self.exec_btn = QPushButton("执行 SQL", self)
        self.layout.addWidget(self.exec_btn)