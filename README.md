# xthulu

Python 3 asyncio terminal server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

[![Coverage Status](https://coveralls.io/repos/github/haliphax/xthulu/badge.svg?branch=master)](https://coveralls.io/github/haliphax/xthulu?branch=master)

## Progress

- [x] SSH server
  - [x] PROXY v1 support
  - [ ] <s>PROXY v2 support</s> _not required for initial release_
  - [ ] SCP subsystem
  - [ ] SFTP subsystem
- [ ] HTTP server
  - [ ] Static files
  - [ ] REST API
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

## Building the docker image

```shell
DOCKER_BUILDKIT=1 docker-compose build app
```

## Starting the services

```shell
docker-compose up -d
```

## Creating/initializing the database

```shell
docker-compose exec app db_create
docker-compose exec app db_init
docker-compose restart app
```

[gino]: https://python-gino.org
