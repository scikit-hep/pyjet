#!/bin/bash

prefix=/usr/local
fastjet_version=3.3.2
fjcontrib_version=1.041

mkdir -p $prefix/src
cd $prefix/src

if [ ! -d fastjet-${fastjet_version} ]; then
    wget http://fastjet.fr/repo/fastjet-${fastjet_version}.tar.gz
    tar xfz fastjet-${fastjet_version}.tar.gz
fi

if [ ! -d fjcontrib-${fjcontrib_version} ]; then
    wget http://fastjet.hepforge.org/contrib/downloads/fjcontrib-${fjcontrib_version}.tar.gz
    tar xfz fjcontrib-${fjcontrib_version}.tar.gz
fi

cd fastjet-${fastjet_version}
make clean
./configure --prefix=$prefix --enable-cgal --enable-allcxxplugins --enable-all-plugins
make -j2
make install
cd ../fjcontrib-${fjcontrib_version}
make clean
./configure --prefix=$prefix --fastjet-config=$prefix/bin/fastjet-config
make -j2
make install
make fragile-shared-install
