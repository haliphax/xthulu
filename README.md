# xthulu Python 3 asyncio terminal server

- [x] SSH server
- [ ] SFTP server
- [ ] HTTP server
- [x] Userland script stack with goto, gosub, exception handling
- [x] Session events queue
  - [ ] Methods for manipulating queue (querying specific events, etc.)
  - [ ] Can target other sessions and send them events (gosub/goto, chat requests, IM, etc.)
- [ ] Server events queue (locks, IPC coordination, etc.)
- [ ] External-to-session IPC (CLI, web, etc.) via Redis PubSub
- [x] PostgreSQL for data
  - [x] Asynchronous ORM ([GINO])
  - [x] User model
  - [ ] Simple pickle table for things like oneliners, automsg, etc.
- [ ] Terminal UI package
  - [x] Isolated `blessed.Terminal` process and proxy
  - [ ] Block editor
  - [ ] Line editor (block editor with a single line)
  - [ ] Lightbar
  - [ ] Vertical lightbar
  - [ ] Matrix (vertical/horizontal lightbar)
  - [ ] Panel (scrollable boundary)

[GINO]: https://python-gino.org
