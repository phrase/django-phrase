## Set up the dev environment
1. `python -m venv env` Set up the virtual environment
2. `source env/bin/activate` Activate the environment
3. `pip install -r requirements.txt` Install dependencies
4. `deactivate` Deactivate environment when done developing

## Releasing a new version of the package
1. `python -m build`
2. `twine upload dist/*`
3. Apply credentials
