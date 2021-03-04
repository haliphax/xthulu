# xthulu

Python 3 asyncio terminal server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

## Progress

- [x] SSH server
- [ ] SFTP server
- [ ] HTTP server
- [x] Userland script stack with goto, gosub, exception handling
- [ ] IPC
  - [x] Session events queue
  - [x] Methods for manipulating queue (querying specific events, etc.)
  - [ ] Can target other sessions and send them events (gosub/goto, chat requests, IM, etc.)
  - [ ] Server events queue (IPC coordination, etc.)
  - [x] Locks (IPC semaphore)
  - [ ] External-to-session IPC (CLI, web, etc.) via Redis PubSub
- [ ] Data layer
  - [x] PostgreSQL for data
  - [x] Asynchronous ORM ([GINO])
  - [x] User model
  - [ ] Message bases
  - [ ] Simple pickle table for things like oneliners, automsg, etc.
- [ ] Terminal UI package
  - [x] Isolated `blessed.Terminal` process and proxy
  - [ ] Block editor
  - [x] Line editor (block editor with a single line)
  - [ ] Lightbar
  - [ ] Vertical lightbar
  - [ ] Matrix (vertical/horizontal lightbar)
  - [ ] Panel (scrollable boundary)


[GINO]: https://python-gino.org
