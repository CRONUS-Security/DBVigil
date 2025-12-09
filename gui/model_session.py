from .base import *
from datetime import datetime

class SessionTableModel(QAbstractTableModel):
    def __init__(self, sessions=None):
        super().__init__()
        self.headers = ["host", "user", "type", "add_time"]
        self.sessions = sessions or []

    def rowCount(self, parent=None):
        return len(self.sessions)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            session = self.sessions[index.row()]
            return session.get(self.headers[index.column()], "")
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def add_session(self, session):
        self.beginInsertRows(self.createIndex(0,0).parent(), len(self.sessions), len(self.sessions))
        session["add_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sessions.append(session)
        self.endInsertRows()

    def remove_session(self, row):
        self.beginRemoveRows(self.createIndex(0,0).parent(), row, row)
        self.sessions.pop(row)
        self.endRemoveRows()
