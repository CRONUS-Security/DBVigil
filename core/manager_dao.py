"""
数据库会话管理DAO，使用SQLite存储会话配置
"""
import sqlite3
import os
from typing import List, Optional
from core.entities import DatabaseSession


class ManagerDao:
    """会话管理数据访问对象"""
    
    def __init__(self, db_path: str = "data.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库和表结构"""
        if not os.path.exists(self.db_path):
            # 创建数据库文件和表
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # 创建数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_type TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    port TEXT NOT NULL,
                    username TEXT,
                    password TEXT,
                    database TEXT,
                    timeout TEXT DEFAULT '60',
                    memo TEXT,
                    is_http TEXT DEFAULT 'false',
                    url TEXT,
                    encryption_key TEXT,
                    is_proxy TEXT DEFAULT 'false',
                    proxy_type TEXT,
                    proxy_address TEXT,
                    proxy_port TEXT,
                    proxy_username TEXT,
                    proxy_password TEXT,
                    http_headers TEXT,
                    connect_type TEXT,
                    add_time TEXT
                )
            ''')
            self.connection.commit()
        else:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
    
    def get_connection(self):
        """获取数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def list_databases(self) -> List[DatabaseSession]:
        """获取所有数据库会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        
        sessions = []
        for row in rows:
            session = DatabaseSession(
                id=row['id'],
                database_type=row['database_type'],
                ip_address=row['ip_address'],
                port=row['port'],
                username=row['username'],
                password=row['password'],
                database=row['database'],
                timeout=row['timeout'],
                memo=row['memo'],
                is_http=row['is_http'],
                url=row['url'],
                encryption_key=row['encryption_key'],
                is_proxy=row['is_proxy'],
                proxy_type=row['proxy_type'],
                proxy_address=row['proxy_address'],
                proxy_port=row['proxy_port'],
                proxy_username=row['proxy_username'],
                proxy_password=row['proxy_password'],
                http_headers=row['http_headers'],
                connect_type=row['connect_type'],
                add_time=row['add_time']
            )
            sessions.append(session)
        
        return sessions
    
    def find_data_by_id(self, session_id: int) -> Optional[DatabaseSession]:
        """根据ID查找数据库会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return DatabaseSession(
                id=row['id'],
                database_type=row['database_type'],
                ip_address=row['ip_address'],
                port=row['port'],
                username=row['username'],
                password=row['password'],
                database=row['database'],
                timeout=row['timeout'],
                memo=row['memo'],
                is_http=row['is_http'],
                url=row['url'],
                encryption_key=row['encryption_key'],
                is_proxy=row['is_proxy'],
                proxy_type=row['proxy_type'],
                proxy_address=row['proxy_address'],
                proxy_port=row['proxy_port'],
                proxy_username=row['proxy_username'],
                proxy_password=row['proxy_password'],
                http_headers=row['http_headers'],
                connect_type=row['connect_type'],
                add_time=row['add_time']
            )
        return None
    
    def add_database(self, session: DatabaseSession) -> int:
        """添加数据库会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data (
                database_type, ip_address, port, username, password, database,
                timeout, memo, is_http, url, encryption_key, is_proxy,
                proxy_type, proxy_address, proxy_port, proxy_username,
                proxy_password, http_headers, connect_type, add_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.database_type, session.ip_address, session.port,
            session.username, session.password, session.database,
            session.timeout, session.memo, session.is_http, session.url,
            session.encryption_key, session.is_proxy, session.proxy_type,
            session.proxy_address, session.proxy_port, session.proxy_username,
            session.proxy_password, session.http_headers, session.connect_type,
            session.add_time
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_database(self, session: DatabaseSession) -> int:
        """更新数据库会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE data SET
                database_type = ?, ip_address = ?, port = ?, username = ?,
                password = ?, database = ?, timeout = ?, memo = ?,
                is_http = ?, url = ?, encryption_key = ?, is_proxy = ?,
                proxy_type = ?, proxy_address = ?, proxy_port = ?,
                proxy_username = ?, proxy_password = ?, http_headers = ?,
                connect_type = ?
            WHERE id = ?
        ''', (
            session.database_type, session.ip_address, session.port,
            session.username, session.password, session.database,
            session.timeout, session.memo, session.is_http, session.url,
            session.encryption_key, session.is_proxy, session.proxy_type,
            session.proxy_address, session.proxy_port, session.proxy_username,
            session.proxy_password, session.http_headers, session.connect_type,
            session.id
        ))
        
        conn.commit()
        return cursor.rowcount
    
    def delete_database(self, session_id: int) -> int:
        """删除数据库会话"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data WHERE id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount
