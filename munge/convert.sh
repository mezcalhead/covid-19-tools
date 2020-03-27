#!/bin/sh

set -e

if [ $# -lt 2 ]; then
  echo "Usage: convert.sh ogr_format outfile"
  echo " example: convert.sh \"ESRI Shapefile\" ../data/data_cleaned.shp"
  exit 1;
fi

export PG_USE_COPY=true

psvfile="../data/data_cleaned.txt"
csvfile="../data/data_cleaned.csv"
outformat="$1"
outfile="$2"

echo "converting $psvfile to $csvfile (pipe separated to tab separated)"
sed  "s/|/\t/g" $psvfile > $csvfile

# TODO Date formatter for LASTUPDATED column in csvt doesn't seem to work

# use ogr2ogr --debug ON ... to troublshoot errors with this command

echo "converting CSV to $outformat using ogr2ogr..."
ogr2ogr -overwrite -progress -s_srs EPSG:4326 -t_srs EPSG:4326 -f "$1" -nlt POINT -oo AUTODETECT_TYPE=YES \
  -oo X_POSSIBLE_NAMES=LON -oo Y_POSSIBLE_NAMES=LAT -lco SPATIAL_INDEX=YES data_cleaned.shp $csvfile  
  
echo "$outfile successfully created"


