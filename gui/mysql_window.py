from gui.base import *
from PySide6.QtCore import QThread, Signal
from core.entities import DatabaseSession
from database.mysql_dao import MysqlDao
import threading


class ConnectionThread(QThread):
    """连接线程"""
    log_signal = Signal(str)
    connected_signal = Signal(bool)
    
    def __init__(self, mysql_dao: MysqlDao):
        super().__init__()
        self.mysql_dao = mysql_dao
    
    def run(self):
        try:
            self.log_signal.emit("正在连接...")
            self.mysql_dao.get_connection()
            self.mysql_dao.get_info()
            self.connected_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"连接失败: {str(e)}")
            self.connected_signal.emit(False)


class CommandThread(QThread):
    """命令执行线程"""
    result_signal = Signal(str)
    log_signal = Signal(str)
    
    def __init__(self, mysql_dao: MysqlDao, command: str, encoding: str):
        super().__init__()
        self.mysql_dao = mysql_dao
        self.command = command
        self.encoding = encoding
    
    def run(self):
        try:
            self.log_signal.emit(f"执行命令: {self.command}")
            result = self.mysql_dao.execute_command(self.command, self.encoding)
            self.result_signal.emit(result)
        except Exception as e:
            self.result_signal.emit(f"执行失败: {str(e)}")


class MysqlWindow(QMainWindow):
    """MySQL操作窗口"""
    
    def __init__(self, session: DatabaseSession):
        super().__init__()
        self.session = session
        self.mysql_dao = MysqlDao(session)
        self.mysql_dao.set_log_callback(self.append_log)
        
        self.setWindowTitle(f"MySQL - {session.ip_address}:{session.port}")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setup_ui()
        
        # 在后台线程中连接
        self.connect_to_database()
    
    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 功能选择区域
        function_group = QGroupBox("功能选择")
        function_layout = QHBoxLayout()
        
        self.udf_btn = QPushButton("UDF提权")
        self.udf_btn.clicked.connect(self.udf_privilege_escalation)
        function_layout.addWidget(self.udf_btn)
        
        self.ntfs_btn = QPushButton("NTFS新建目录(win)")
        function_layout.addWidget(self.ntfs_btn)
        
        self.clean_btn = QPushButton("痕迹清理")
        self.clean_btn.clicked.connect(self.clean_traces)
        function_layout.addWidget(self.clean_btn)
        
        function_layout.addStretch()
        function_group.setLayout(function_layout)
        main_layout.addWidget(function_group)
        
        # Windows反弹Shell区域
        reverse_group = QGroupBox("Windows 反弹 Shell")
        reverse_layout = QHBoxLayout()
        
        reverse_layout.addWidget(QLabel("回连地址:"))
        self.reverse_address_edit = QLineEdit()
        reverse_layout.addWidget(self.reverse_address_edit)
        
        reverse_layout.addWidget(QLabel("回连端口:"))
        self.reverse_port_edit = QLineEdit()
        reverse_layout.addWidget(self.reverse_port_edit)
        
        self.reverse_btn = QPushButton("Go!")
        reverse_layout.addWidget(self.reverse_btn)
        
        reverse_group.setLayout(reverse_layout)
        main_layout.addWidget(reverse_group)
        
        # 标签页区域
        self.tab_widget = QTabWidget()
        
        # 命令执行标签页
        command_tab = QWidget()
        command_layout = QVBoxLayout(command_tab)
        
        # 命令输入区域
        command_input_layout = QHBoxLayout()
        
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("输入系统命令...")
        command_input_layout.addWidget(self.command_edit)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "GB2312", "GBK"])
        command_input_layout.addWidget(self.encoding_combo)
        
        self.exec_btn = QPushButton("执行")
        self.exec_btn.clicked.connect(self.execute_command)
        command_input_layout.addWidget(self.exec_btn)
        
        command_layout.addLayout(command_input_layout)
        
        # 命令输出区域
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        command_layout.addWidget(self.command_output)
        
        self.tab_widget.addTab(command_tab, "命令执行")
        
        main_layout.addWidget(self.tab_widget)
        
        # 日志输出区域
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        log_layout.addWidget(self.log_output)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        self.setCentralWidget(central_widget)
    
    def connect_to_database(self):
        """连接到数据库"""
        self.conn_thread = ConnectionThread(self.mysql_dao)
        self.conn_thread.log_signal.connect(self.append_log)
        self.conn_thread.connected_signal.connect(self.on_connected)
        self.conn_thread.start()
    
    def on_connected(self, success: bool):
        """连接完成回调"""
        if success:
            self.append_log("数据库连接成功，可以开始操作")
        else:
            self.append_log("数据库连接失败")
    
    def append_log(self, message: str):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
    
    def execute_command(self):
        """执行系统命令"""
        command = self.command_edit.text().strip()
        if not command:
            QMessageBox.warning(self, "提示", "请输入命令")
            return
        
        encoding = self.encoding_combo.currentText().lower()
        if encoding == "gb2312":
            encoding = "gb2312"
        elif encoding == "gbk":
            encoding = "gbk"
        else:
            encoding = "utf-8"
        
        self.command_output.clear()
        self.command_output.append(f"执行命令: {command}\n")
        
        # 在后台线程中执行
        self.cmd_thread = CommandThread(self.mysql_dao, command, encoding)
        self.cmd_thread.result_signal.connect(self.on_command_result)
        self.cmd_thread.log_signal.connect(self.append_log)
        self.cmd_thread.start()
    
    def on_command_result(self, result: str):
        """命令执行结果回调"""
        self.command_output.append(result)
    
    def udf_privilege_escalation(self):
        """UDF提权"""
        reply = QMessageBox.question(
            self, "UDF提权",
            "UDF提权需要上传UDF库文件到服务器，是否继续？\n\n"
            "注意：此功能需要MySQL用户具有FILE权限",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.append_log("开始 UDF 提权...")
            
            # 在后台线程中执行
            thread = threading.Thread(target=self._do_udf_privilege)
            thread.daemon = True
            thread.start()
    
    def _do_udf_privilege(self):
        """执行UDF提权"""
        try:
            result = self.mysql_dao.udf_privilege_escalation()
            if result:
                self.append_log("UDF 提权成功")
            else:
                self.append_log("UDF 提权失败或不支持")
        except Exception as e:
            self.append_log(f"UDF 提权异常: {str(e)}")
    
    def clean_traces(self):
        """清理痕迹"""
        reply = QMessageBox.question(
            self, "清理痕迹",
            "确定要清理所有自定义函数和临时文件吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.append_log("开始清理痕迹...")
            
            # 在后台线程中执行
            thread = threading.Thread(target=self._do_clean_traces)
            thread.daemon = True
            thread.start()
    
    def _do_clean_traces(self):
        """执行清理痕迹"""
        try:
            self.mysql_dao.clean_traces()
            self.append_log("痕迹清理完成")
        except Exception as e:
            self.append_log(f"清理痕迹失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.mysql_dao.close_connection()
        event.accept()
