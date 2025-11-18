# Feature check list

## Terminal server

- [x] <s>SSH server ([AsyncSSH][])</s>
  - [x] <s>Password authentication</s>
  - [x] <s>Guest (no-auth) users</s>
  - [ ] Key authentication
- [x] <s>PROXY v1 support</s>
- [ ] SFTP subsystem
- [x] <s>Composite userland script stack</s>
  - [x] <s>Goto</s>
  - [x] <s>Gosub</s>
  - [x] <s>Exception handling</s>
- [x] <s>Terminal library ([rich][])</s>
  - [x] <s>Adapt for SSH session usage</s>
- [ ] UI components ([textual][])
  - [x] <s>Adapt for SSH session usage</s>
  - [ ] File browser
  - [ ] Message interface
    - [x] <s>List messages</s>
    - [x] <s>Post messages</s>
    - [x] <s>Reply to messages</s>
    - [x] <s>Tag system</s>
    - [x] <s>Filter by tag(s)</s>
    - [ ] Search messages
    - [ ] Private messages
- [ ] Door games
  - [x] <s>Subprocess redirect for terminal apps</s>
  - [ ] Dropfile generators
    - [ ] `DOOR.SYS`
    - [ ] `DORINFOx.DEF`

## Miscellaneous

- [x] <s>Container proxy ([Traefik][])</s>
- [x] <s>HTTP server ([uvicorn][])</s>
  - [x] <s>Basic authentication</s>
  - [x] <s>Web framework ([FastAPI][])</s>
    - [x] <s>Composite userland</s>
  - [x] <s>Static files</s>
- [ ] IPC
  - [x] <s>Session events queue</s>
  - [x] <s>Methods for manipulating queue (querying specific events, etc.)</s>
  - [ ] Can target other sessions and send them events (gosub/goto, chat
        requests, IM, etc.)
  - [ ] Server events queue (IPC coordination, etc.)
  - [x] <s>Locks (IPC semaphore)</s>
  - [x] <s>Global IPC (CLI, web, etc.) via Redis PubSub</s>
- [ ] Data layer
  - [x] <s>PostgreSQL for data</s>
  - [x] <s>Asynchronous ORM ([SQLModel][])</s>
  - [x] <s>User model</s>
  - [x] <s>Message bases</s>
  - [ ] Simple JSONB table for mixed use
- [ ] Permissions
  - [ ] User groups
  - [ ] ACLs system

[asyncssh]: https://asyncssh.readthedocs.io/en/latest/
[fastapi]: https://fastapi.tiangolo.com
[rich]: https://rich.readthedocs.io/en/latest/
[sqlmodel]: https://sqlmodel.tiangolo.com/
[textual]: https://github.com/Textualize/textual
[traefik]: https://traefik.io/traefik
[uvicorn]: https://www.uvicorn.org
