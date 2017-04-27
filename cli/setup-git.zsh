#!/usr/bin/env zsh
sudo userdel -r git -f
sudo useradd -m git
sudo usermod -s $(command -v git-shell) git
sudo loginctl enable-linger git
cmd() {
	echo "> $*"
	sudo -u git $*
}
dir=~git/git-shell-commands
cmd mkdir $dir
pushd commands >/dev/null
for file in $(command dir); do
	cmd tee $dir/$file < $file
	cmd chmod u+x $dir/$file
done
popd >/dev/null
cmd mkdir ~git/.ssh
echo "Please input the public key(s) used for authentication."
echo "Press <C-D> when done."
cmd tee ~git/.ssh/authorized_keys >/dev/null
