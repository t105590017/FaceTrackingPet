# FaceTrackingPet
畢業專題

Prepare the virtual environment before dev
The file is in the VirtualenvSetupFiles folder

# Install Virtualenv And Libary
    sudo apt install python3-pip
    pip3 install virtualenv

## Create a new python3.7 virtual environment
    virtualenv PythonVirtualenv --python=python3.7

## Activating Virtual Environment
    source ./PythonVirtualenv/bin/activate

## Install All Of The Packages In requirement.txt
    pip install -r requirement.txt

## Exit virtual environment
    deactivate