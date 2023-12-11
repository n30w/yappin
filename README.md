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

## Goals

- Extensibility
- Maintainability
- Stateless

The goals for this project is to ensure that this code is as extensible and as maintainable as possible. That means in the future, someone can pick up this code base and continue to work on it easily. "Stateless" just means that we are going to try and avoid maintaining and changing object state as much as possible, to ensure easy code debugging and headache avoidance. It also makes the code easier to read. As far as I know, chat programs *need* stative components, so this is just to limit them as much as possible.

## Required Dependencies

- Protobuf
- Taskfile
- Tkinter
- rsa
- cryptography
- grpcio-tools
- grpclib
- betterproto

## Notes

- Client.py serves as the entry point for the client program. Server.py serves as the entry point for the server program.
- Please use type safety!
- The Taskfile.yml is used to synchronize commands and build without having to resort to many command line command executions.
- Use protobuf compiler with ```protoc -I . --python_betterproto_out=. example.proto```
- User commands are always preceded by a ```/```
- Chat histories are NOT stored on server. Only P2P.

## Improvements

- Can use separate API calls given different protobuf type

## Style Convention

- Good practice is to use type assertions rather than implicit types. This makes code more readable and lets the developer carry less mental load when debugging.
- Private attributes are denoted by ```__```, or the double underscore before its name.
