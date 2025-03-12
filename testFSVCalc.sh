#!/bin/sh

sleep 1
rm -fv ../output/running/runlog-test1.html
rm -fvr ../output/results/test1/
sleep 1
./runFSVCalc.py --jobid=test1 --pdbid=1ehz
