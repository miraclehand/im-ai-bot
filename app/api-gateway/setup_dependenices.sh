source venv/bin/activate
pip freeze > requirements.txt
pip download -r requirements.txt -d ./packages
