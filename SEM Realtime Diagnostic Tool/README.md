Instructions for using/developing the software on Windows.
Using VS Code for the developing is not compulsory, but I like it.

Liuchuyao Xu, 2019

Installations:
    Install Python
        Add Python to PATH when installing.
    Install Qt5
        Only the source component is needed.
    Install VS Code
        Install Python extension.

Developing the software in VS Code:
    Open the project folder.
    Open the file "SEMTool.py".
    Use powershell for the terminal.
    In the terminal, run
        python3 -m venv .venv
        .venv/Scripts/activate.bat
            (.venv) should show up in the terminal if the virtual environment has been successfully activated.
            If the virtual environment is not activated, try clicking the green triangular button at the top right corner of "SEMTool.py".
    Select '.venv':venv as the environment at the bottom left corner.
    In the terminal, run
        pip install pylint
        pip install Pillow
        pip install numpy
        pip install PySide2
