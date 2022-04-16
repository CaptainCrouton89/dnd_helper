echo "Installing necessary packages"
pip install -r requirements.txt

echo "Installing app"
mkdir ~/Applications/dnd_helper_pi
cp -R . ~/Applications/dnd_helper_pi

echo "Appending to .zshrc file to allow run"
echo "source ~/Applications/dnd_helper_pi/run.sh" >> ~/.zshrc

echo "
=======================================
Installed

use 'gen -h' to see possible commands
======================================="
