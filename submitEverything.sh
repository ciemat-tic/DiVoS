#!/bin/sh

for file in $(ls inputFiles)
do
       sh submit_kepler.sh inputFiles/$file
done




