pgzero runs only with python 3.6, on linux mint 20 only python 3.8 is available.

This the way:

https://tecadmin.net/install-python-3-6-ubuntu-linuxmint/

Step 1 – Prerequsities

sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

Step 2 – Download Python 3.6

cd /usr/src
sudo wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
sudo tar xzf Python-3.6.10.tgz


Step 3 – Compile Python Source

cd Python-3.6.10
sudo ./configure --enable-optimizations
sudo make altinstall


Step 4 – Check the Python Version

python3.6 -V

pip3.6 -V
