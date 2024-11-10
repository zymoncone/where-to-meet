# 📍 Where to Meet

After graduation, my friends and I dispersed across the US, making reunions a logistical challenge. Every time, one of us ends up stuck with the tedious task of scouring _Google Flights_, _Airbnb_, and _Vrbo_ to figure out the best and most financially savvy travel plan for everyone. But what if there was a tool to simplify this process? Introducing _Where2Meet_ – the ultimate solution for finding the perfect meeting spot for your group.

This tool takes the locations of you and your friends as input, along with your travel dates. It calculates a geographic midpoint, then creates a radius to identify the closest airports within that area. From there, it explores all possible flight combinations and retrieves prices for each route. The tool then optimizes the results to ensure that, on average, everyone gets the best possible deal.

The potential for _Where2Meet_ is limitless. As we continue to develop, we'll add even more parameters for users to fine-tune, making the tool even smarter and more customizable.

Discover the best destinations effortlessly at [Where2Meet](https://where2meet.streamlit.app/).

## Installation

This app requires `Python 3.8+`

### Create a virtual environment

```sh
python -m venv .venv
```

### Activate the virtual environment

```sh
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

Once activated, you will see your environment's name in parentheses at the beginning of your terminal prompt `(.venv)`

### Install packages

You can install it all your packages directly from `requirements.txt`

```sh
pip install -r requirements.txt
```

### Run your Streamlit app.

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
