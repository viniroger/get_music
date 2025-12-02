#!/bin/bash

CEL1_IP="192.168.15.20"
CEL2_IP="192.168.15.40"
PORT=8022
SRC="/home/vinicius/Música/"

for IP in $CEL1_IP $CEL2_IP; do
    echo "Sincronizando com $IP..."
    rsync -azvh --delete -e "ssh -p $PORT" "$SRC" \
        u0_aXYZ@"$IP":~/storage/music/
done
