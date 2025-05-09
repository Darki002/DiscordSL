class SessionError(RuntimeError):
    pass

class MaxSessionsError(SessionError):
    pass

class UserHasSessionError(SessionError):
    pass