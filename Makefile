VENV = source venv/bin/activate &&

venv: requirements.txt scripts/requirements.txt
	virtualenv venv -p python3
	$(VENV) pip install -r requirements.txt

