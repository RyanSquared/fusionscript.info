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

## iptables

The below rules will forward port 25562 to 443 (TLS for the webserver) and port
25563 for 80 (plaintext for certbot domain authentication).

```sh
$ sudo -s
# iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 25562
# iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 25563
```

### Extra Files

Files found in the `etc` directory can be useful for configuring the
website for your file system. The files are almost entirely OS independent.

```
systemd/system/fs-renew-certs.service
systemd/system/fs-auto-renew-certs.timer
systemd/system/fs-serve-static-web.service
```

These services (which start at multi-user, as does the website itself) will
install certificates from a Let's Encrypt directory into the `~git/ssl`
directory for the website to use. Make sure to modify the service files if
you use a different domain. The included timer can be enabled to attempt a
renewal (if required) hourly. Renewals are usually done if the certificate will
expire in less than 30 days.

Also, as a note, use
`sudo certbot certonly --webroot -w /home/git/web -d fusionscript.info`
to receive the initial certificate.

These files should be installed in `/etc/systemd/system/`.

```
bin/renew-certs-post
```

This script is required by the `fs-renew-certs` service file to automatically
install certificates as the `git` user. When run, the script will install the
certificates for the `$RENEWED_DOMAINS` domain list into ~git/ssl. Make sure to
modify the script so that the domain in the script (`fusionscript.info`)
matches the one currently used in your deployment.

This file should be installed in `/usr/local/bin`.
