import datetime

from shared.enums import Action


class StdoutLogger:
    @staticmethod
    def log(message: str) -> None:
        """
        Logs a message with a timestamp to standard output.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    @staticmethod
    def user_action(username: str, action: Action) -> None:
        msg = f"(USER ACTION) :: {action} :: @{username}"
        StdoutLogger.log(msg)
