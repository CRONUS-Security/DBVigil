from .base import *
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from gui.add_session_dialog import AddSessionDialog
from core.manager_dao import ManagerDao
from core.entities import DatabaseSession


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBVigil - 数据库管理工具")
        self.setGeometry(100, 100, 900, 650)

        # 初始化数据访问对象
        self.manager_dao = ManagerDao()

        # 创建中心部件
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建表格视图
        self.table = QTableView(self)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.open_database_action)

        # 设置表格模型
        self.setup_table_model()

        # 设置右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        main_layout.addWidget(self.table)

        # 创建状态栏
        self.status_label = QLabel("暂无信息")
        self.status_label.setStyleSheet("padding: 3px;")

        self.author_label = QLabel("By: DBVigil Team")
        self.author_label.setAlignment(Qt.AlignRight)
        self.author_label.setStyleSheet("padding: 3px;")

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(3, 0, 3, 0)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.author_label)
        status_widget.setMaximumHeight(24)

        main_layout.addWidget(status_widget)

        self.setCentralWidget(central_widget)

        # 加载数据
        self.refresh_table()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        setting_action = QAction("设置", self)
        file_menu.addAction(setting_action)

        file_menu.addSeparator()

        close_action = QAction("关闭", self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        doc_action = QAction("使用文档", self)
        help_menu.addAction(doc_action)

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_table_model(self):
        """设置表格模型"""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "IP", "数据库类型", "连接类型", "备忘", "添加时间"])
        self.table.setModel(self.model)

        # 设置列宽
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 200)

    def refresh_table(self):
        """刷新表格数据"""
        self.model.removeRows(0, self.model.rowCount())

        sessions = self.manager_dao.list_databases()
        for session in sessions:
            row = [
                QStandardItem(str(session.id)),
                QStandardItem(session.ip_address),
                QStandardItem(session.database_type),
                QStandardItem(session.connect_type),
                QStandardItem(session.memo),
                QStandardItem(session.add_time),
            ]

            # 设置居中对齐
            for item in row:
                item.setTextAlignment(Qt.AlignCenter)

            self.model.appendRow(row)

        self.status_label.setText(f"共 {len(sessions)} 个会话")

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_database_action)
        menu.addAction(open_action)

        add_action = QAction("新增", self)
        add_action.triggered.connect(self.add_database_action)
        menu.addAction(add_action)

        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.edit_database_action)
        menu.addAction(edit_action)

        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_database_action)
        menu.addAction(delete_action)

        menu.addSeparator()

        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.refresh_table)
        menu.addAction(refresh_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def open_database_action(self):
        """打开数据库会话"""
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "提示", "请先选择一个会话")
            return

        # 获取选中行的ID
        row = index.row()
        session_id = int(self.model.item(row, 0).text())
        session = self.manager_dao.find_data_by_id(session_id)

        if session:
            # 根据数据库类型打开对应窗口
            if session.database_type == "Mysql":
                from gui.mysql_window import MysqlWindow

                self.db_window = MysqlWindow(session)
                self.db_window.show()
            elif session.database_type == "Mssql":
                QMessageBox.information(self, "提示", "MSSQL 功能暂未实现")
            elif session.database_type == "PostgreSql":
                QMessageBox.information(self, "提示", "PostgreSQL 功能暂未实现")
            else:
                QMessageBox.warning(self, "提示", f"不支持的数据库类型: {session.database_type}")

    def add_database_action(self):
        """添加数据库会话"""
        dialog = AddSessionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            session = dialog.get_session_data()
            if session:
                self.manager_dao.add_database(session)
                self.refresh_table()
                self.status_label.setText("添加会话成功")

    def edit_database_action(self):
        """编辑数据库会话"""
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "提示", "请先选择一个会话")
            return

        # 获取选中行的ID
        row = index.row()
        session_id = int(self.model.item(row, 0).text())
        session = self.manager_dao.find_data_by_id(session_id)

        if session:
            dialog = AddSessionDialog(self, session)
            if dialog.exec() == QDialog.Accepted:
                updated_session = dialog.get_session_data()
                if updated_session:
                    updated_session.id = session_id
                    self.manager_dao.update_database(updated_session)
                    self.refresh_table()
                    self.status_label.setText("更新会话成功")

    def delete_database_action(self):
        """删除数据库会话"""
        index = self.table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "提示", "请先选择一个会话")
            return

        reply = QMessageBox.question(self, "确认删除", "确定要删除选中的会话吗?", QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            row = index.row()
            session_id = int(self.model.item(row, 0).text())
            self.manager_dao.delete_database(session_id)
            self.refresh_table()
            self.status_label.setText("删除会话成功")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 DBVigil",
            "DBVigil - 数据库管理工具\n\n"
            "版本: 1.0.0\n"
            "基于 MDUT 项目改造\n\n"
            "支持的数据库:\n"
            "  - MySQL\n"
            "  - MSSQL (开发中)\n"
            "  - PostgreSQL (开发中)",
        )
