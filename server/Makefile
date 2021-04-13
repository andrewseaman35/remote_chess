VENV = source venv/bin/activate &&

venv: requirements.txt
	virtualenv venv -p python3
	$(VENV) pip install -r requirements.txt

start_local:
	export FLASK_APP=flaskr; \
	export FLASK_ENV=development; \
	$(VENV) flask run
