"""
数据库会话实体类
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DatabaseSession:
    """数据库会话实体类"""
    id: Optional[int] = None
    database_type: str = "Mysql"  # Mysql, Mssql, PostgreSql
    ip_address: str = ""
    port: str = ""
    username: str = ""
    password: str = ""
    database: str = ""
    timeout: str = "60"
    memo: str = ""
    is_http: str = "false"  # 是否使用HTTP通道
    url: str = ""
    encryption_key: str = ""
    is_proxy: str = "false"  # 是否使用代理
    proxy_type: str = ""
    proxy_address: str = ""
    proxy_port: str = ""
    proxy_username: str = ""
    proxy_password: str = ""
    http_headers: str = ""
    connect_type: str = "直连"  # 直连或HTTP
    add_time: str = ""
    
    def __post_init__(self):
        if not self.add_time:
            self.add_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 根据是否使用HTTP设置连接类型
        if self.is_http != "false":
            self.connect_type = "HTTP"
        else:
            self.connect_type = "直连"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'database_type': self.database_type,
            'ip_address': self.ip_address,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'database': self.database,
            'timeout': self.timeout,
            'memo': self.memo,
            'is_http': self.is_http,
            'url': self.url,
            'encryption_key': self.encryption_key,
            'is_proxy': self.is_proxy,
            'proxy_type': self.proxy_type,
            'proxy_address': self.proxy_address,
            'proxy_port': self.proxy_port,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'http_headers': self.http_headers,
            'connect_type': self.connect_type,
            'add_time': self.add_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(**data)
