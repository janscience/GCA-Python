#!/bin/sh

if [ $# -ne 1 ]; then
  echo "Wrong number of arguments! Usag: $0 path"
  exit -1
fi

OLDPWD=`pwd`
cd $1

for f in *.gif; do
    echo "converting $f"
    convert "$f[0]" "${f/%gif/png}"
done

cd "$OLDPWD"