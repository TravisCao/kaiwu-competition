#!/bin/bash

# usage: build_code.sh
# env: OUTPUT_DIR, default is ./build
# env: OUTPUT_FILENAME, default is code-$version.tgz

version=2.3.0-`date +"%Y%m%d%H%M"`
filename=code-$version.tgz

# current shell script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$(dirname $SCRIPT_DIR)
TMP_DIR="/tmp/train/"

output_dir=${OUTPUT_DIR:-"./build"}
output_dir=$( cd -- "$output_dir" &> /dev/null && pwd )
filename=${OUTPUT_FILENAME:-"code-$version.tgz"}

# reset build code dir
rm -f $output_dir/*.tgz
rm -rf $TMP_DIR && mkdir -p $TMP_DIR


# build code
rsync -a --exclude="checkpoints_*" \
         --exclude="**/checkpoints" \
         --exclude="**/algorithms/checkpoint" \
         $ROOT_DIR/code $TMP_DIR
cp -r $ROOT_DIR/scripts $TMP_DIR

# remove unused files
rm -rf $TMP_DIR/code/battle

# generate version
echo "$version" > $TMP_DIR/version

# 打包
cd $TMP_DIR && tar -czf $output_dir/$filename . && cd -