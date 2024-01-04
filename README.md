**Create an environment**
`python -m venv .venv`

**Activate the environment**
`.venv\Scripts\activate`
> if error, run this first: `Set-ExecutionPolicy Unrestrict -Scope Process`

**Install library**
`pip install -r .\requirements.txt`

**Run flask**
`flask --app flaskr run --debug`