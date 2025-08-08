# Project SOAR Data Lake Generator
This program imports data from the original spreadsheet file for Project SOAR and turns that into a JSON file for use by the static frontend.

## Instructions
There are two ways to use this: either compile the code (or download the official binary), or use the Python virtual environment (venv) to run with the interpreter.

### Method 2: Run via interpreter in virtual environment (venv)
1. Create a Python virtual environment with venv.

```shell
python -m venv venv
```

2. Source the virtual environment.

```shell
source venv/bin/activate
```
3. Install dependencies.

```shell
pip install -r requirements.txt
```

4. Run te application.

```shell
python main.py
```
