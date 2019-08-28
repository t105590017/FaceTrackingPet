# install python&pip first, then execute the following code with cmd

    sudo apt install python3-pip
    pip3 install virtualenv
    virtualenv ..\PythonVirtualenv --python=python3.7
    ..\PythonVirtualenv\Scripts\activate
    pip install -r requirement.txt
    ..\PythonVirtualenv\Scripts\deactivate
