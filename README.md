# xthulu

Python 3 asyncio community server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

[![Coverage Status](https://coveralls.io/repos/github/haliphax/xthulu/badge.svg?branch=master)](https://coveralls.io/github/haliphax/xthulu?branch=master)

While **xthulu** is intended to be a _community_ server which will provide
multiple avenues of interaction (e.g. web, terminal), its primary focus is in
providing a modern SSH terminal server akin to the [bulletin boards] of old.

## Progress

### Terminal server

<details>
<summary>Click to expand</summary>

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

### Other

<details>
<summary>Click to expand</summary>

- [ ] HTTP server
  - [ ] Static files
  - [ ] REST API
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

</details>

## Usage

ℹ️ Commands which involve `docker` or `docker-compose` must be run from the
`docker/` directory of the repository in order for the command to locate the
YAML configuration file(s). Other commands assume you are in the repository's
root directory.

### Build the docker image

```shell
DOCKER_BUILDKIT=1 docker-compose build app
```

### Create a configuration file and generate host keys

```shell
cp data/config.example.toml data/config.toml
ssh-keygen -f data/ssh_host_key -t rsa -b 4096  # do not use a key password
```

### Create and seed the database

```shell
docker-compose run --rm app db-create
docker-compose run --rm app db-init
docker-compose run --rm --entrypoint python app -m userland.cli.seed
```

### Start the services

```shell
docker-compose up -d
```

### Connect to the guest account

```shell
ssh guest@localhost
```

[bulletin boards]: https://archive.org/details/BBS.The.Documentary
[gino]: https://python-gino.org
