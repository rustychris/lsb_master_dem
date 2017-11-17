#!/bin/bash

if [ -z $1 ] ; then
  echo "Must give path argument"
  exit 1
fi

cd $1

gdal_merge.py -init nan -a_nodata nan -o merged_2m.tif 5*.tif
