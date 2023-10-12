# xthulu

xthulu _("ch-THOO-loo")_ Python 3 asyncio community server

![Header image](https://github.com/haliphax/xthulu/raw/assets/xthulu.jpg)

[![Build](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/docker-build.yml?label=Build)](https://github.com/haliphax/xthulu/actions/workflows/docker-build.yml)
[![Checks](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/checks.yml?label=Checks)](https://github.com/haliphax/xthulu/actions/workflows/checks.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/tests.yml?label=Tests)](https://github.com/haliphax/xthulu/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/coverallsCoverage/github/haliphax/xthulu?label=Coverage)](https://coveralls.io/github/haliphax/xthulu)

While **xthulu** is intended to be a _community_ server which will provide
multiple avenues of interaction (e.g. terminal, browser, REST API), its primary
focus is in providing a modern SSH terminal interface which pays homage to the
[bulletin boards][] of the 1990s. Rather than leaning entirely into [DOS][]-era
nostalgia, modern character sets (UTF-8) and [terminal capabilities][] are taken
advantage of.

- [Contributor guide][]

## Progress

<details>
<summary>Terminal server checklist</summary>

### Terminal server

- [x] SSH server ([AsyncSSH][])
  - [x] Password authentication
  - [x] Guest (no-auth) users
  - [ ] Key authentication
- [x] PROXY v1 support
- [ ] SCP subsystem
- [ ] SFTP subsystem
- [x] Userland script stack
  - [x] Goto
  - [x] Gosub
  - [x] Exception handling
- [x] Terminal library ([rich][])
  - [x] Adapt for SSH session usage
- [ ] UI components ([textual][])
  - [x] Adapt for SSH session usage
  - [ ] File browser
  - [ ] Message interface

</details>

<details>
<summary>Miscellaneous checklist</summary>

### Miscellaneous

- [x] Container proxy ([Traefik][])
- [ ] HTTP server ([uvicorn][])
  - [x] Userland
  - [x] Static files
  - [ ] REST API
    - [x] Web framework ([APIFlask][])
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
  - [x] Asynchronous ORM ([GINO][])
  - [x] User model
  - [ ] Message bases
  - [ ] Simple pickle table ("The Pile") for miscellaneous data storage

</details>

## Setup

### Build the docker images

```shell
# in the docker/ directory
docker compose build
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
docker compose run --rm ssh db-create
docker compose run --rm ssh db-init
docker compose run --rm --entrypoint python ssh -m userland.cli.seed
```

### Start the services

```shell
# in the docker/ directory
docker compose up -d
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
between the REST API and static pages. It is available at https://localhost. The
userland web interface is at https://localhost/user.

⚠️ [Traefik][] will be using an untrusted certificate, and you will likely be
presented with a warning.

[apiflask]: https://apiflask.com
[asyncssh]: https://asyncssh.readthedocs.io/en/latest/
[blessed]: https://blessed.readthedocs.io/en/latest/intro.html
[bulletin boards]: https://archive.org/details/BBS.The.Documentary
[contributor guide]: ./CONTRIBUTING.md
[dos]: https://en.wikipedia.org/wiki/MS-DOS
[gino]: https://python-gino.org
[rich]: https://rich.readthedocs.io/en/latest/
[terminal capabilities]: https://en.wikipedia.org/wiki/Terminal_capabilities
[textual]: https://github.com/Textualize/textual
[traefik]: https://traefik.io/traefik
[uvicorn]: https://www.uvicorn.org
