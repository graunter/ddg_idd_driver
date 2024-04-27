#!/bin/bash

ARCHITECTURE="armhf"
PROJECT_NAME="ddg-idd-driver"
VERSION="1.0.11"
BUILD_PLATFORM_ADDRESS=$1
BUILD_PLATFORM_PORT=$2
BUILD_PLATFORM_PASS=$3

# Info: you need sshpass packet for this script:
# sudo apt-get install sshpass

#build machine settings:
USER="root"
BUILD_PATH="~/build_dir_$PROJECT_NAME"
DIST_PATH="~/build_dir_$PROJECT_NAME/dist"

OUTPUT_PATH="../../build/$ARCHITECTURE"
EXE_OUTPUT_PATH="$OUTPUT_PATH/package/opt/$PROJECT_NAME"
EXE_NAME=$PROJECT_NAME

# rm $EXE_OUTPUT_PATH/$EXE_NAME 2> /dev/null
# rm ../../build/${PROJECT_NAME}_${VERSION}_${ARCHITECTURE}.deb 2> /dev/null
rm -rf $OUTPUT_PATH

#copy source to build platform:
cmd="mkdir -p $BUILD_PATH"
sshpass -p $BUILD_PLATFORM_PASS ssh $USER@$BUILD_PLATFORM_ADDRESS -p $BUILD_PLATFORM_PORT "$cmd" 
sshpass -p $BUILD_PLATFORM_PASS scp -P $BUILD_PLATFORM_PORT ../src/*.* $USER@$BUILD_PLATFORM_ADDRESS:$BUILD_PATH

#compile source
cmd="pyinstaller --onefile $BUILD_PATH/main.py -n '$EXE_NAME' --specpath $BUILD_PATH --distpath $DIST_PATH"
sshpass -p $BUILD_PLATFORM_PASS ssh $USER@$BUILD_PLATFORM_ADDRESS -p $BUILD_PLATFORM_PORT "$cmd" 

echo "coping result to local path..."
mkdir -p $EXE_OUTPUT_PATH
sshpass -p $BUILD_PLATFORM_PASS scp -P $BUILD_PLATFORM_PORT $USER@$BUILD_PLATFORM_ADDRESS:$DIST_PATH/$EXE_NAME $EXE_OUTPUT_PATH

# echo "cleaning remote path..."
# cmd="rm -rf $BUILD_PATH"
# ssh $USER@$BUILD_PLATFORM_ADDRESS -p $BUILD_PLATFORM_PORT "$cmd" 

cp -a package $OUTPUT_PATH
version=$(cat $OUTPUT_PATH/package/DEBIAN/control | grep 'Version:' | awk '{print$2}')
dpkg-deb --root-owner-group -b $OUTPUT_PATH/package "$OUTPUT_PATH/ddg-idd-driver_${version}_${ARCHITECTURE}.deb"