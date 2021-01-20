#!/usr/bin/env bash
set -e

pushd .
cd "$HOME" || exit 1
echo "pwd: $(pwd )"
df -h
df -h .
rm -rf linux_amd64.tar.gz weed
wget --quiet https://github.com/chrislusf/seaweedfs/releases/download/2.21/linux_amd64.tar.gz
tar xf linux_amd64.tar.gz
rm -f linux_amd64.tar.gz
chmod +x weed
mkdir -p data/volume1 data/volume2
./weed master -ip 127.0.0.1 -port 9333 >weed_master.log 2>&1 &
./weed volume -dir="./data/volume1" -max=5 -mserver="127.0.0.1:9333" -ip 127.0.0.1 -port=27000 >weed_volume_1.log 2>&1 &
./weed volume -dir="./data/volume2" -max=5 -mserver="127.0.0.1:9333" -ip 127.0.0.1 -port=27001 >weed_volume_2.log 2>&1 &
./weed filer -ip 127.0.0.1 -port=27100 -master="127.0.0.1:9333" >weed_filer.log 2>&1 &
sleep 10
ls -alh
echo "cat weed_master.log" && cat weed_master.log
echo "weed_volume_1.log" && cat weed_volume_1.log
echo "weed_volume_2.log" && cat weed_volume_2.log
echo "weed_filer.log" && cat weed_filer.log
echo "Done cat"
echo "started all weed services"
echo "pwd is $(pwd)"
ls -alh
popd
echo "pwd: $(pwd )"
