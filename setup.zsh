#!/bin/zsh

# Create the `git` user and install command line utilities
pushd cli
./setup-git.sh
popd

# Install the `fs-info` package
pushd web
sudo -u git pip3 install --user .
popd

# Preparing for launch
sudo -u git mkdir -p ~git/{repos,web,.config/fs-info,ssl}

# Systemd service file
sudo tee /etc/systemd/system/fs-info-website.service <<EOF
[Unit]
Description=FusionScript website, in Python 3
Requires=network.target

[Service]
User=git
WorkingDirectory=/home/git
ExecStart=/usr/bin/python3 -m fs-info
Restart=always
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF


# Copy over SSL files
sudo -u git tee ~git/ssl/cert.pem >/dev/null < ssl/cert.pem
sudo -u git tee ~git/ssl/key.pem >/dev/null < ssl/key.pem

# Webserver configuration
PORT=${PORT:=25562}
BINDHOST=${BINDHOST:=0.0.0.0}
sudo -u git tee ~git/.config/fs-info/conf.json <<EOF
{
	"address": "${BINDHOST}",
	"port": ${PORT},
	"compress_response": true,
	"ssl_options": {
	    "certfile": "ssl/cert.pem",
	    "keyfile": "ssl/key.pem"
	}
}
EOF

# Copy over webserver static files
sudo cp -r web/{templates,static} ~git/
sudo chown -R git:git ~git/{templates,static}

# Launch the website
sudo systemctl enable --now fs-info-website.service
sudo systemctl restart fs-info-website.service
