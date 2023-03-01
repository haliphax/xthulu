# xthulu

Python 3 asyncio community server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

[![Coverage Status](https://coveralls.io/repos/github/haliphax/xthulu/badge.svg?branch=master)](https://coveralls.io/github/haliphax/xthulu?branch=master)

While **xthulu** is intended to be a _community_ server which will provide
multiple avenues of interaction (e.g. web, terminal), its primary focus is in
providing a modern SSH terminal server which pays homage to the
[bulletin boards] of the 1990s. Rather than leaning entirely into [DOS]-era
nostalgia, modern character sets (UTF-8) and [terminal capabilities] are taken
advantage of.

- [Contributor guide]

## Progress

<details>
<summary>Terminal server checklist</summary>

### Terminal server

- [x] SSH server
- [x] PROXY v1 support
- [ ] SCP subsystem
- [ ] SFTP subsystem
- [x] Userland script stack
  - [x] Goto
  - [x] Gosub
  - [x] Exception handling
- [x] Isolated `blessed.Terminal` process and proxy
- [ ] UI components
  - [ ] Block editor
  - [x] Line editor (block editor with a single line)
  - [ ] Lightbar
  - [ ] Vertical lightbar
  - [ ] Matrix (vertical/horizontal lightbar)
  - [ ] Panel (scrollable boundary)

</details>

<details>
<summary>Miscellaneous checklist</summary>

### Miscellaneous

- [ ] HTTP server
  - [ ] Static files
  - [ ] REST API
- [ ] IPC
  - [x] Session events queue
  - [x] Methods for manipulating queue (querying specific events, etc.)
  - [ ] Can target other sessions and send them events (gosub/goto, chat
        requests, IM, etc.)
  - [ ] Server events queue (IPC coordination, etc.)
  - [x] Locks (IPC semaphore)
  - [ ] External-to-session IPC (CLI, web, etc.) via Redis PubSub
- [ ] Data layer
  - [x] PostgreSQL for data
  - [x] Asynchronous ORM ([GINO])
  - [x] User model
  - [ ] Message bases
  - [ ] Simple pickle table for things like oneliners, automsg, etc.

</details>

## Usage

ℹ️ Commands which involve `docker` or `docker-compose` must be run from the
`docker/` directory of the repository in order for the command to locate the
YAML configuration file(s). Other commands assume you are in the repository's
root directory.

### Build the docker image

```shell
DOCKER_BUILDKIT=1 docker-compose build ssh
```

### Create a configuration file and generate host keys

```shell
cp data/config.example.toml data/config.toml
ssh-keygen -f data/ssh_host_key -t rsa -b 4096  # do not use a key password
```

### Create and seed the database

```shell
docker-compose run --rm ssh db-create
docker-compose run --rm ssh db-init
docker-compose run --rm --entrypoint python ssh -m userland.cli.seed
```

### Start the services

```shell
docker-compose up -d
```

### Connect to the terminal server

There is a `guest` account which demonstrates the ability for some accounts to
bypass authentication.

```shell
ssh guest@localhost
```

There is also an account with a password for testing password authentication.

- username: `user`
- password: `user`

[bulletin boards]: https://archive.org/details/BBS.The.Documentary
[dos]: https://en.wikipedia.org/wiki/MS-DOS
[terminal capabilities]: https://en.wikipedia.org/wiki/Terminal_capabilities
[contributor guide]: ./CONTRIBUTING.md
[gino]: https://python-gino.org
