## Installation

```sh
export PYTHON=$(which python3)
export PORT=25562
export BINDHOST=0.0.0.0
export CERTFILE=ssl/cert.pem
export KEYFILE=ssl/key.pem
export DB_URI=sqlite://
export DB_USER=user
export DB_PASS=pass
zsh setup.zsh
```

### Variables:

`PYTHON` - path to Python 3.6 interpreter

`PORT` - Port to run on (443 for TLS without specifying port in URLs)

`BINDHOST` - Address to bind server to (`0.0.0.0` is all addresses)

`CERTFILE` - PEM file containing TLS certificates

`KEYFILE` - PEM file containing a TLS private key

`DB_URI` - URI for database to use

`DB_USER` - Username for database (if not SQLite)

`DB_PASS` - Password for database (if not SQLite)

`DB_NAME` - URL for database (`*.db` if SQLite)

**Note about databases**

Using, for example, postgresql with the website requires a format for a
username and a password for the URI. The URI needs to be set up using the
SQLAlchemy format, such as `postgresql://{user}:{pass}@localhost:25563/{name}`.
The database, if SQLite is not used, will have to be set up manually before the
`setup.zsh` script is run, and the program does not make backups automatically.
