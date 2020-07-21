#!/bin/bash
##### Untar Function
if [ ! -d "./spectra/" ] 
then
    echo "Directory ./spectra/ does not exist. Creating."
    mkdir ./spectra/
else
    echo "Unpacking into ./spectra/"
fi
tar -xf spectra.tar -C ./spectra/
cd ./spectra/
for g in *.gz
    do 
    STEM=$(basename "${g}" .gz)
    gunzip -c "${g}" > ./"${STEM}"
    done
rm *.gz
echo "Unpacked."
##### Friendly Reminders
echo "Feel free to generate data from SONORA."
echo "Please remember to update your configuration files."