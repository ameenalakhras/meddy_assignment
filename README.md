# meddy_assignment

This repo is an assignment to meddy to collecte the news from different sources like (reddit, apinews)
and return all the services apis responses them as a one response with the same unified data.

### 1. Create a python virtual environment
`virtualenv -p /usr/bin/python3.8 venv`

### 2. Move to the python virtual environment
`source venv/bin/activate`

### 3. Rename .env_example to .env and add the environment variables in it.
`mv .env_example .env`

### 4. Install the project requirements:
`pip install -r requirements.txt`

### 5. Run the project run:
`uvicorn main:app --reload`

## to check the requests endpoints head to:
- http://127.0.0.1:8000/docs