#!/bin/zsh

setopt -x

PYTHON=${PYTHON:=$(which python3)}
PORT=${PORT:=25562}
BINDHOST=${BINDHOST:=0.0.0.0}
CERTFILE=${CERTFILE:=ssl/cert.pem}
KEYFILE=${CERTFILE:=ssl/key.pem}
DB_URI=${DB_URI:=sqlite://}

# Create the `git` user and install command line utilities
pushd cli
./setup-git.zsh
popd

# Install the `fs-info` package
pushd web
sudo -H -u git ${PYTHON} -m pip install --user .
popd

# Preparing for launch
sudo -u git mkdir -p ~git/{repos{,/rendered},web,.config/fs-info,ssl}

# Systemd service file
sudo tee /etc/systemd/system/fs-info-website.service <<EOF
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

sudo tee /etc/systemd/system/git-daemon.service <<EOF
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


# Copy over SSL files
sudo -u git tee ~git/ssl/cert.pem >/dev/null < ${CERTFILE}
sudo -u git tee ~git/ssl/key.pem >/dev/null < ${KEYFILE}

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
sudo cp -r web/{templates,static} ~git/
sudo chown -R git:git ~git/{templates,static}

# Launch the website
sudo systemctl enable fs-info-website.service
sudo systemctl enable git-daemon.service
sudo systemctl restart git-daemon.service

echo "Please make sure to run \`sudo systemctl enable fs-info-website.service\`"
echo "after installing certificate and key to ~git/ssl"
