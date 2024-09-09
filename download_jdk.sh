#!/bin/bash

set -ex

wget https://aka.ms/download-jdk/microsoft-jdk-17.0.12-linux-x64.tar.gz
tar -xf microsoft-jdk-17.0.12-linux-x64.tar.gz
mv jdk-17.0.12+7 jdk
rm -f microsoft-jdk-17.0.12-linux-x64.tar.gz