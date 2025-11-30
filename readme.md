## Dependencies
Requirements can be installed the usual way:  
`pip install -r requirements.txt`

For a dev environment also run:
`pip install -r requirements_dev.txt`

For maintaining and updating requirements we use `pip-tools`

 The main libraries are defined in `requirements.in`

 `pip-compile requirements.in` will generate a new `requirements.txt`.

 *Do **not** update the `requirements.txt` by hand!* 
