Creating the virtual environment in the root folder:
1. `python -m venv env` Set up the virtual environment
2. `source env/bin/activate` Activate the environment

Once you have created the virtual environment in the parent folder:
1. Cd to this folder
2. run `pip install ../.` to install the local (most up to date) version of the integration
1. Run `python manage.py runserver`
2. Navigate to `http://127.0.0.1:8000/ice_demo/`
3. Login with `demo@phrase.com` / `phrase`
