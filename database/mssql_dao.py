"""
MSSQL 数据库操作 DAO (占位符 - 待实现)
"""
from core.entities import DatabaseSession
from typing import Optional, Callable


class MssqlDao:
    """MSSQL数据库访问对象 (占位符)"""
    
    def __init__(self, session: DatabaseSession):
        """初始化MSSQL连接"""
        self.session = session
        self.connection = None
        self.log_callback: Optional[Callable] = None
    
    def set_log_callback(self, callback: Callable):
        """设置日志回调函数"""
        self.log_callback = callback
    
    def log(self, message: str):
        """输出日志"""
        if self.log_callback:
            self.log_callback(message)
    
    def get_connection(self):
        """获取数据库连接 (待实现)"""
        self.log("MSSQL 功能暂未实现")
        raise NotImplementedError("MSSQL 功能暂未实现")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
