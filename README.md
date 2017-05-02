## Requirements

- `python3.6` compatible interpreter
- a way to install TLS certificates

## Installation

```sh
# These are used for the webserver
export PYTHON=$(which python3)
export PORT=25562
export BINDHOST=0.0.0.0

# Change these values to reflect your database location
# This uses SQLAlchemy URI format
# Keep this as it is if you want
export DB_URI=sqlite://{name}
export DB_USER=user
export DB_PASS=pass
export DB_NAME=fs_info.db

# Set these for manual certificate installation
export CERTFILE=ssl/cert.pem
export KEYFILE=ssl/key.pem

# Set these for automatic certificate installation (certbot)
export DOMAIN=fusionscript.info
export WITH_CERTBOT=true
export HTTP_PORT=25563 # Shouldn't need to change this

# Set this if the `git` user can't use port 443 - it'll automatically
# be redirected by iptables
export WITH_IPTABLES=true

zsh setup.zsh
EOF
```

### Variables

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
