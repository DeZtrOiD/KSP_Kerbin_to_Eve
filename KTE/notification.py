
import krpc

def notify(conn: krpc.Client, message: str) -> None:
    print(message)
    conn.ui.message(content = message, duration = 8)
