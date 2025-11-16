# xthulu

xthulu _("ch-THOO-loo")_ Python asyncio community server

![Header image](https://github.com/haliphax/xthulu/raw/assets/banner.jpg)

[![Build](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/docker-build.yml?label=Build)](https://github.com/haliphax/xthulu/actions/workflows/docker-build.yml)
[![Checks](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/checks.yml?label=Checks)](https://github.com/haliphax/xthulu/actions/workflows/checks.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/haliphax/xthulu/tests.yml?label=Tests)](https://haliphax.testspace.com/spaces/318003?utm_campaign=metric&utm_medium=referral&utm_source=badge)
[![Coverage](https://img.shields.io/coverallsCoverage/github/haliphax/xthulu?label=Coverage)](https://coveralls.io/github/haliphax/xthulu)

While **xthulu** is intended to be a _community_ server with multiple avenues of
interaction (e.g. terminal, browser, REST API), its primary focus is to provide
a modern SSH terminal interface which pays tribute to the [bulletin boards][] of
the 1990s. Rather than leaning entirely into [DOS][]-era nostalgia, modern
character sets (UTF-8) and [terminal capabilities][] are taken advantage of.

- 📔 [Contributor guide][]
- 📽️ [Demo video][] (animated GIF)

## Progress

- 📊 [Alpha release project board][]
- ✅ [Feature check list][]

## Setup

```shell
# in the project root
bin/setup
```

<details>
<summary>Manual steps</summary>

---

If you want to perform the steps in the setup script manually for some reason,
here they are:

### Create a configuration file and generate host keys

```shell
# in the data/ directory
cp config.example.toml config.toml
ssh-keygen -f ssh_host_key -t rsa -b 4096 -N ""
```

### Prepare the docker images

```shell
# in the docker/ directory
docker compose build base-image
docker compose pull --ignore-buildable
```

### Create and seed the database

> ℹ️ Note the names of the scripts. The `bin/xt` script is the command line
> interface for server tasks, while the `bin/xtu` script is for userland.

```shell
# in the project root
bin/xt db create --seed
bin/xtu db create --seed
```

### Build the static web assets

```shell
# in the project root
bin/build-web
```

---

</details>

### Start the services

```shell
# in the docker/ directory
docker compose up -d
```

## Connect

### Connect to the terminal server

There is a `guest` account which demonstrates the ability for some accounts to
bypass authentication.

```shell
ssh guest@localhost
```

There is a `user` account with a password for testing password authentication.

```shell
ssh user@localhost  # password is also "user"
```

### Connect to the web server

For the time being, the web server only demonstrates simple interoperability
between the REST API and static pages. It is available at https://localhost.
There is a demo application that can be used for chatting with other users
connected via both the web and the SSH server.

> ⚠️ [Traefik][] will be using an untrusted certificate, and you will likely be
> presented with a warning.

The same credentials may be used here; for the `guest` account, any password (or
a blank password) will work.

[alpha release project board]: https://github.com/users/haliphax/projects/1
[blessed]: https://blessed.readthedocs.io/en/latest/intro.html
[bulletin boards]: https://archive.org/details/BBS.The.Documentary
[contributor guide]: ./CONTRIBUTING.md
[demo video]: https://github.com/haliphax/xthulu/raw/assets/demo.gif
[dos]: https://en.wikipedia.org/wiki/MS-DOS
[feature check list]: ./CHECKLIST.md
[terminal capabilities]: https://en.wikipedia.org/wiki/Terminal_capabilities
[traefik]: https://traefik.io/traefik
