import datetime


class StdoutLogger:
    def log(self, message: str) -> None:
        """
        Logs a message with a timestamp to standard output.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
