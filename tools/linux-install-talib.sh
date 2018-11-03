#!/bin/bash

pkg_name="ta-lib-0.4.0-src.tar.gz"

echo "installing talib ${pkg_name} for python pip ta-lib"
cd /tmp

echo "getting ta-lib: http://prdownloads.sourceforge.net/ta-lib/${pkg_name}"
wget http://prdownloads.sourceforge.net/ta-lib/${pkg_name}
ls /tmp/${pkg_name}

echo "extracting /tmp/${pkg_name} to /opt"
cd /opt
tar xvf /tmp/${pkg_name}

if [[ ! -e /opt/ta-lib ]]; then
    echo "failed to find /opt/ta-lib directory after extracting: tar xvf /tmp/${pkg_name}"
    echo "this could be your user does not have permissions to /opt"
    exit 1
else
    echo "starting ta-lib source build in dir: /opt/ta-lib"
fi

cd /opt/ta-lib

echo "configuring ta-lib with /usr"
./configure --prefix=/usr

echo "making ta-lib"
make

echo "installing ta-lib"
make install

exit 0
