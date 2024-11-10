# Where to Meet ✈️📍

|Module Version| |Build Status| |Maintainability| |Dependencies|


## Installation

This app requires Python 3.8+

1. Create a virtual environment

```sh
python -m venv .venv
```

2. Activate the virtual environment

```sh
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

Once activated, you will see your environment's name in parentheses at the beginning of your terminal prompt. "(.venv)"

3. Install packages

You can install it all your packages directly from `requirements.txt`

```sh
pip install -r requirements.txt
```

4. Run your Streamlit app.

```sh
streamlit run app.py
```

If this doesn't work, use the long-form command

```sh
python -m streamlit run app.py
```

To stop the Streamlit server, press `Ctrl+C` in the terminal.

When you're done using this environment, return to your normal shell by typing

```sh
deactivate
```