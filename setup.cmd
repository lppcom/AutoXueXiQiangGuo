@echo off
cd /d %~dp0
echo %cd%
echo first, confirm python3.7+ installed?
echo install venv...
python -m venv venv
REM echo venv installed OK.
echo install packages...

REM venv\scripts\python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install Appium-Python-Client -i https://pypi.tuna.tsinghua.edu.cn/simple

REM venv\scripts\python -m pip install appium -i https://pypi.tuna.tsinghua.edu.cn/simple appium客户端请手动安装，自行百度appium安装

venv\scripts\python -m pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install fuzzywuzzy -i https://pypi.tuna.tsinghua.edu.cn/simple

venv\scripts\python -m pip install python-Levenshtein -i https://pypi.tuna.tsinghua.edu.cn/simple

REM echo packages installed OK.

pause