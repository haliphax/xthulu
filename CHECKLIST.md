# Feature check list

## Terminal server

- [x] SSH server ([AsyncSSH][])
  - [x] Password authentication
  - [x] Guest (no-auth) users
  - [ ] Key authentication
- [x] PROXY v1 support
- [ ] SFTP subsystem
- [x] Composite userland script stack
  - [x] Goto
  - [x] Gosub
  - [x] Exception handling
- [x] Terminal library ([rich][])
  - [x] Adapt for SSH session usage
- [ ] UI components ([textual][])
  - [x] Adapt for SSH session usage
  - [ ] File browser
  - [ ] Message interface
    - [x] List messages
    - [x] Post messages
    - [x] Reply to messages
    - [x] Tag system
    - [x] Filter by tag(s)
    - [ ] Search messages
    - [ ] Private messages
- [ ] Door games
  - [x] Subprocess redirect for terminal apps
  - [ ] Dropfile generators
    - [ ] `DOOR.SYS`
    - [ ] `DORINFOx.DEF`

## Miscellaneous

- [x] Container proxy ([Traefik][])
- [x] HTTP server ([uvicorn][])
  - [x] Basic authentication
  - [x] Web framework ([FastAPI][])
    - [x] Composite userland
  - [x] Static files
- [ ] IPC
  - [x] Session events queue
  - [x] Methods for manipulating queue (querying specific events, etc.)
  - [ ] Can target other sessions and send them events (gosub/goto, chat
        requests, IM, etc.)
  - [ ] Server events queue (IPC coordination, etc.)
  - [x] Locks (IPC semaphore)
  - [ ] Global IPC (CLI, web, etc.) via Redis PubSub
- [ ] Data layer
  - [x] PostgreSQL for data
  - [x] Asynchronous ORM ([SQLModel][])
  - [x] User model
  - [x] Message bases
  - [ ] Simple JSONB table for mixed use

[asyncssh]: https://asyncssh.readthedocs.io/en/latest/
[fastapi]: https://fastapi.tiangolo.com
[rich]: https://rich.readthedocs.io/en/latest/
[sqlmodel]: https://sqlmodel.tiangolo.com/
[textual]: https://github.com/Textualize/textual
[traefik]: https://traefik.io/traefik
[uvicorn]: https://www.uvicorn.org
