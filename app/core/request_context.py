from contextvars import ContextVar

trace_id_var: ContextVar[str] = ContextVar("trace_id")
user_id_var: ContextVar[str] = ContextVar("user_id")

def set_trace_id(trace_id: str) -> None:
    trace_id_var.set(trace_id)
    
def set_user_id(user_id: str) -> None:
    user_id_var.set(user_id)


def get_trace_id() -> str:
    return trace_id_var.get()

def get_user_id() -> str:
    return user_id_var.get()


