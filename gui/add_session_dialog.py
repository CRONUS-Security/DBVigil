from .base import *


class AddSessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加 Session")
        self.setFixedSize(300, 220)
        layout = QVBoxLayout(self)

        self.host_edit = QLineEdit(self)
        self.port_edit = QLineEdit(self)
        self.user_edit = QLineEdit(self)
        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["MySQL", "SQLServer"])

        layout.addWidget(QLabel("Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_edit)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_edit)
        layout.addWidget(QLabel("User:"))
        layout.addWidget(self.user_edit)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定", self)
        self.cancel_btn = QPushButton("取消", self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return {
            "host": self.host_edit.text().strip(),
            "user": self.user_edit.text().strip(),
            "type": self.type_combo.currentText(),
        }
