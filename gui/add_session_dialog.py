from .base import *
from core.entities import DatabaseSession
from datetime import datetime


class AddSessionDialog(QDialog):
    """添加/编辑会话对话框"""
    
    def __init__(self, parent=None, session: DatabaseSession = None):
        super().__init__(parent)
        self.session = session
        self.is_edit_mode = session is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("编辑会话")
        else:
            self.setWindowTitle("添加会话")
        
        self.setMinimumSize(500, 600)
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_session_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 常规标签页
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "常规")
        
        # HTTP标签页
        self.http_tab = self.create_http_tab()
        self.tab_widget.addTab(self.http_tab, "HTTP")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.status_label = QLabel("")
        button_layout.addWidget(self.status_label)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_action)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """创建常规标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # 数据库类型
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["Mysql", "Mssql", "PostgreSql"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        layout.addRow("数据库类型:", self.db_type_combo)
        
        # IP地址
        self.ip_edit = QLineEdit()
        layout.addRow("地址:", self.ip_edit)
        
        # 端口
        self.port_edit = QLineEdit("3306")
        layout.addRow("端口:", self.port_edit)
        
        # 用户名
        self.username_edit = QLineEdit("root")
        layout.addRow("用户:", self.username_edit)
        
        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("密码:", self.password_edit)
        
        # 数据库
        self.database_edit = QLineEdit()
        layout.addRow("数据库:", self.database_edit)
        
        # 超时
        self.timeout_edit = QLineEdit("60")
        layout.addRow("超时(秒):", self.timeout_edit)
        
        # 备忘
        self.memo_edit = QTextEdit()
        self.memo_edit.setMaximumHeight(150)
        layout.addRow("备忘:", self.memo_edit)
        
        return widget
    
    def create_http_tab(self):
        """创建HTTP标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 是否使用HTTP通道
        self.use_http_check = QCheckBox("是否使用 HTTP 通道")
        self.use_http_check.stateChanged.connect(self.on_http_check_changed)
        layout.addWidget(self.use_http_check)
        
        # HTTP配置区域
        http_group = QGroupBox()
        http_layout = QFormLayout(http_group)
        
        self.url_edit = QLineEdit()
        self.url_edit.setEnabled(False)
        http_layout.addRow("通道地址:", self.url_edit)
        
        self.key_edit = QLineEdit()
        self.key_edit.setEnabled(False)
        http_layout.addRow("加密密钥:", self.key_edit)
        
        self.headers_edit = QTextEdit()
        self.headers_edit.setEnabled(False)
        self.headers_edit.setMaximumHeight(100)
        http_layout.addRow("自定义请求头:", self.headers_edit)
        
        layout.addWidget(http_group)
        
        # 是否使用代理
        self.use_proxy_check = QCheckBox("是否使用代理(非HTTP模式无效)")
        self.use_proxy_check.setEnabled(False)
        self.use_proxy_check.stateChanged.connect(self.on_proxy_check_changed)
        layout.addWidget(self.use_proxy_check)
        
        # 代理配置区域
        proxy_group = QGroupBox()
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS5"])
        self.proxy_type_combo.setEnabled(False)
        proxy_layout.addRow("类型:", self.proxy_type_combo)
        
        self.proxy_address_edit = QLineEdit()
        self.proxy_address_edit.setEnabled(False)
        proxy_layout.addRow("地址:", self.proxy_address_edit)
        
        self.proxy_port_edit = QLineEdit()
        self.proxy_port_edit.setEnabled(False)
        proxy_layout.addRow("端口:", self.proxy_port_edit)
        
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setEnabled(False)
        proxy_layout.addRow("用户名:", self.proxy_username_edit)
        
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        self.proxy_password_edit.setEnabled(False)
        proxy_layout.addRow("密码:", self.proxy_password_edit)
        
        layout.addWidget(proxy_group)
        layout.addStretch()
        
        return widget
    
    def on_db_type_changed(self, db_type):
        """数据库类型改变时的处理"""
        if db_type == "Mysql":
            self.port_edit.setText("3306")
            self.username_edit.setText("root")
            self.username_edit.setEnabled(True)
            self.database_edit.setEnabled(True)
        elif db_type == "Mssql":
            self.port_edit.setText("1433")
            self.username_edit.setText("sa")
            self.username_edit.setEnabled(True)
            self.database_edit.setEnabled(True)
        elif db_type == "PostgreSql":
            self.port_edit.setText("5432")
            self.username_edit.setText("postgres")
            self.username_edit.setEnabled(True)
            self.database_edit.setEnabled(True)
    
    def on_http_check_changed(self, state):
        """HTTP通道复选框状态改变"""
        enabled = state == Qt.Checked
        self.url_edit.setEnabled(enabled)
        self.key_edit.setEnabled(enabled)
        self.headers_edit.setEnabled(enabled)
        self.use_proxy_check.setEnabled(enabled)
        
        if not enabled:
            self.use_proxy_check.setChecked(False)
    
    def on_proxy_check_changed(self, state):
        """代理复选框状态改变"""
        enabled = state == Qt.Checked
        self.proxy_type_combo.setEnabled(enabled)
        self.proxy_address_edit.setEnabled(enabled)
        self.proxy_port_edit.setEnabled(enabled)
        self.proxy_username_edit.setEnabled(enabled)
        self.proxy_password_edit.setEnabled(enabled)
    
    def load_session_data(self):
        """加载会话数据（用于编辑模式）"""
        if not self.session:
            return
        
        # 常规标签
        self.db_type_combo.setCurrentText(self.session.database_type)
        self.ip_edit.setText(self.session.ip_address)
        self.port_edit.setText(self.session.port)
        self.username_edit.setText(self.session.username)
        self.password_edit.setText(self.session.password)
        self.database_edit.setText(self.session.database)
        self.timeout_edit.setText(self.session.timeout)
        self.memo_edit.setPlainText(self.session.memo)
        
        # HTTP标签
        if self.session.is_http != "false":
            self.use_http_check.setChecked(True)
            self.url_edit.setText(self.session.url)
            self.key_edit.setText(self.session.encryption_key)
            self.headers_edit.setPlainText(self.session.http_headers)
        
        if self.session.is_proxy != "false":
            self.use_proxy_check.setChecked(True)
            self.proxy_type_combo.setCurrentText(self.session.proxy_type)
            self.proxy_address_edit.setText(self.session.proxy_address)
            self.proxy_port_edit.setText(self.session.proxy_port)
            self.proxy_username_edit.setText(self.session.proxy_username)
            self.proxy_password_edit.setText(self.session.proxy_password)
    
    def test_connection(self):
        """测试数据库连接"""
        self.status_label.setText("正在测试连接...")
        QApplication.processEvents()
        
        # 获取当前输入的会话数据
        session = self.get_session_data()
        if not session:
            return
        
        try:
            if session.database_type == "Mysql":
                import pymysql
                conn = pymysql.connect(
                    host=session.ip_address,
                    port=int(session.port),
                    user=session.username,
                    password=session.password,
                    database=session.database,
                    connect_timeout=int(session.timeout)
                )
                conn.close()
                self.status_label.setText("✓ 连接成功")
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText("该数据库类型暂不支持测试")
                self.status_label.setStyleSheet("color: orange;")
        except Exception as e:
            self.status_label.setText(f"✗ 连接失败: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def save_action(self):
        """保存会话"""
        session = self.get_session_data()
        if session:
            self.accept()
    
    def get_session_data(self) -> DatabaseSession:
        """获取会话数据"""
        # 验证必填字段
        if not self.ip_edit.text().strip():
            QMessageBox.warning(self, "提示", "IP地址不能为空")
            return None
        
        if not self.username_edit.text().strip():
            QMessageBox.warning(self, "提示", "用户名不能为空")
            return None
        
        # 创建会话对象
        session = DatabaseSession(
            database_type=self.db_type_combo.currentText(),
            ip_address=self.ip_edit.text().strip(),
            port=self.port_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text(),
            database=self.database_edit.text().strip(),
            timeout=self.timeout_edit.text().strip(),
            memo=self.memo_edit.toPlainText().strip(),
            is_http="true" if self.use_http_check.isChecked() else "false",
            url=self.url_edit.text().strip(),
            encryption_key=self.key_edit.text().strip(),
            is_proxy="true" if self.use_proxy_check.isChecked() else "false",
            proxy_type=self.proxy_type_combo.currentText(),
            proxy_address=self.proxy_address_edit.text().strip(),
            proxy_port=self.proxy_port_edit.text().strip(),
            proxy_username=self.proxy_username_edit.text().strip(),
            proxy_password=self.proxy_password_edit.text()
        )
        
        return session
