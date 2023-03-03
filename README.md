# xthulu

xthulu _("ch-thoo-loo")_ Python 3 asyncio community server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

[![Tests](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/tests.yml?label=Tests)](https://github.com/haliphax/xthulu/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/coverallsCoverage/github/haliphax/xthulu?label=Coverage)](https://coveralls.io/github/haliphax/xthulu)

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

- [x] SSH server ([AsyncSSH])
- [x] PROXY v1 support
- [ ] SCP subsystem
- [ ] SFTP subsystem
- [x] Userland script stack
  - [x] Goto
  - [x] Gosub
  - [x] Exception handling
- [x] Terminal library ([Blessed])
  - [x] Process-isolated `Terminal` to circumvent atomic `TERM`
- [ ] UI components
  - [x] Block editor
  - [x] Line editor (block editor with a single line)
  - [ ] Horizontal lightbar
  - [ ] Vertical lightbar
  - [ ] Matrix (vertical/horizontal lightbar)
  - [ ] Panel (scrollable boundary)

</details>

<details>
<summary>Miscellaneous checklist</summary>

### Miscellaneous

- [x] Container proxy ([Traefik])
- [ ] HTTP server
  - [x] Static files
  - [ ] REST API
    - [x] Web framework ([APIFlask])
    - [ ] Implementation
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
  - [x] Asynchronous ORM ([GINO])
  - [x] User model
  - [ ] Message bases
  - [ ] Simple pickle table ("The Pile") for miscellaneous data storage

</details>

## Setup

### Build the docker image

```shell
# in the docker/ directory
DOCKER_BUILDKIT=1 docker-compose build
```

### Create a configuration file and generate host keys

```shell
# in the repository root
cp data/config.example.toml data/config.toml
ssh-keygen -f data/ssh_host_key -t rsa -b 4096  # do not use a passphrase
```

### Create and seed the database

```shell
# in the docker/ directory
docker-compose run --rm ssh db-create
docker-compose run --rm ssh db-init
docker-compose run --rm --entrypoint python ssh -m userland.cli.seed
```

### Start the services

```shell
# in the docker/ directory
docker-compose up -d
```

### Connect to the terminal server

There is a `guest` account which demonstrates the ability for some accounts to
bypass authentication.

```shell
ssh guest@localhost
```

There is also an account with a password for testing password authentication.

```shell
ssh user@localhost  # password is also "user"
```

### Connect to the web server

For the time being, the web server only demonstrates simple interoperability
between the REST API and static pages. It is available at https://localhost.

⚠️ [Traefik] will be using an untrusted certificate, and you will likely be
presented with a warning.

[bulletin boards]: https://archive.org/details/BBS.The.Documentary
[dos]: https://en.wikipedia.org/wiki/MS-DOS
[terminal capabilities]: https://en.wikipedia.org/wiki/Terminal_capabilities
[contributor guide]: ./CONTRIBUTING.md
[asyncssh]: https://asyncssh.readthedocs.io/en/latest/
[blessed]: https://blessed.readthedocs.io/en/latest/intro.html
[traefik]: https://traefik.io/traefik
[apiflask]: https://apiflask.com
[gino]: https://python-gino.org
