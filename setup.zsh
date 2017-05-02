#!/bin/zsh

setopt -x

[ "$UID" -eq 0 ] || exec sudo zsh "$0"

PYTHON=${PYTHON:=$(which python3)}
PORT=${PORT:=25562}
BINDHOST=${BINDHOST:=0.0.0.0}
DOMAIN=${DOMAIN:=fusionscript.info}
CERTFILE=${CERTFILE:=ssl/cert.pem}
KEYFILE=${CERTFILE:=ssl/key.pem}
DB_URI=${DB_URI:=sqlite://}
HTTP_PORT=${HTTP_PORT:=25563}
WITH_IPTABLES=${WITH_IPTABLES:=true}
WITH_CERTBOT=${WITH_CERTBOT:=true}

# Set up iptables rules
if $WITH_IPTABLES; then
	iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port ${PORT}
	iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port ${HTTP_PORT}
fi

# Create the `git` user and install command line utilities
pushd cli
./setup-git.zsh
popd

# Set up certbot
if $WITH_CERTBOT; then
	cp etc/systemd/system/* /etc/systemd/system
	systemctl enable fs-serve-static-web.service
	systemctl enable fs-renew-certs.service
	systemctl enable fs-auto-renew-certs.timer
	tee /usr/local/bin/renew-certs-post < etc/bin/renew-certs-post
	chmod u+x /usr/local/bin/renew-certs-post
	systemctl start fs-serve-static-web.service
	mkdir web
	pushd web
	$PYTHON -m http.server ${HTTP_PORT}
	server_pid=$!
	certbot certonly --webroot -w $PWD -d ${DOMAIN}
	kill $server_pid
	popd
	rmdir web
	systemctl start fs-auto-renew-certs.timer
	systemctl restart fs-renew-certs.service
fi

# Install the `fs-info` package
pushd web
sudo -H -u git ${PYTHON} -m pip install --user .
popd

# Preparing for launch
sudo -u git mkdir -p ~git/{repos{,/rendered},web,.config/fs-info,ssl}

# Systemd service file
tee /etc/systemd/system/fs-info-website.service <<EOF
[Unit]
Description=FusionScript website, in Python 3
Requires=network.target

[Service]
User=git
WorkingDirectory=/home/git
ExecStart=${PYTHON} -m fs-info
Restart=always
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

tee /etc/systemd/system/git-daemon.service <<EOF
[Unit]
Description=Automatically start git-daemon
Requires=network.target

[Service]
User=git
WorkingDirectory=/home/git/repos
ExecStart=/usr/bin/git daemon --base-path=/home/git --export-all
Restart=always
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF


# Copy over TLS files if certbot is not used
if ! ${WITH_CERTBOT}; then
	sudo -u git tee ~git/ssl/cert.pem >/dev/null < ${CERTFILE}
	sudo -u git tee ~git/ssl/key.pem >/dev/null < ${KEYFILE}
fi

# Webserver configuration
sudo -u git tee ~git/.config/fs-info/conf.json <<EOF
{
	"address": "${BINDHOST}",
	"port": ${PORT},
	"compress_response": true,
	"ssl_options": {
		"certfile": "ssl/cert.pem",
		"keyfile": "ssl/key.pem"
	},
	"db": {
		"uri": "${DB_URI}",
		"user": "${DB_USER}",
		"pass": "${DB_PASS}",
		"name": "${DB_NAME}"
	}

}
EOF

# Copy over webserver static files
cp -r web/{templates,static} ~git/
chown -R git:git ~git/{templates,static}

# Launch the website
systemctl enable fs-info-website.service
systemctl enable git-daemon.service
systemctl restart fs-info-website.service
systemctl restart git-daemon.service
