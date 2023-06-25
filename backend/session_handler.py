from collections import defaultdict
from uuid import uuid4
from datetime import datetime, timedelta
from config import SESSION_EXPIRE_MINUTES

class Session_Handler():

    def __init__(self, session_expiring_period=SESSION_EXPIRE_MINUTES) -> None:
        self.sessions = defaultdict(dict)
        self.session_expiring_period = session_expiring_period  # minutes

    def create_new_session(self) -> str:
        new_session_id = str(uuid4())
        self.sessions[new_session_id]['created_at'] = datetime.now()
        return new_session_id

    def get_session_information(self, session_id) -> object:
        return self.sessions[session_id]

    def add_informations(self, session_id, dictionary) -> None:
        for k, v in dictionary.items():
            self.add_information(session_id, k, v)

    def add_information(self, session_id, key, value) -> None:
        self.sessions[session_id][key] = value

    def check_if_key_isthere(self, session_id, key) -> bool:
        return key in self.sessions[session_id]

    def clean_old_sessions(self):
        keys = self.sessions.keys()
        for session in keys:
            if self.is_old(self.sessions[session]['created_at']):
                del self.sessions[session]

    def is_old(self, datetime_) -> bool:
        return datetime.now() - datetime_ > timedelta(minutes=self.session_expiring_period)