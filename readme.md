## Dependencies
Requirements can be installed the usual way after having created a venv and making certain it is active.  
`pip install -r requirements.txt`

For a dev environment also run:
`pip install -r requirements_dev.txt`

For maintaining and updating requirements we use `pip-tools`

 The main libraries are defined in `requirements.in`. This is the file you maintain by hand.

 `pip-compile --upgrade requirements.in` will generate a new *requirements.txt* based on *requirements.in*.

 `pip-sync` will bring the venv in sync with the specified requirements. This includes uninstalling libraries which are no longer needed. By default it will look for *requirements.txt*.

*requirements_dev.txt* has `-c requirements.txt` at the top so running `pip-sync requirements_dev.txt` does not uninstall any libraries mentioned in *requirements.txt* but excluded in *requirements_dev.txt*.

 > Do **not** update the *requirements.txt* by hand! 
