# yappin

ICS Fall 2023 Final. Name is based on "yapping", English word for talking annoyingly.

Python ```3.12.0``` required for new ```type``` usage. There is no backwards compatibility.

## Ideas

- Verified E2EE with emojis like Telegram calls
- Server-based chatting system, not P2P
- SQLite database, storing chat messages
- Protobuf to send messages
- Search chat feature
- Send pictures and videos

## Required Dependencies

- Protobuf
- Taskfile

## Notes

- Client.py serves as the entry point for the client program. Server.py serves as the entry point for the server program.
- Please use type safety!
- The Taskfile.yml is used to synchronize commands and build without having to resort to many command line command executions.

## Style Convention

- Good practice is to use type assertions rather than implicit types. This makes code more readable and lets the developer carry less mental load when debugging.
- Private attributes are denoted by ```__```, or the double underscore before its name.
