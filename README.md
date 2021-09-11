# meddy_assignment

## Description 

This repo is an assignment to Meddy to collect the news from different sources like [**Reddit**](https://www.reddit.com/dev/api/ "Reddit") and [**News API**](https://newsapi.org/ "News API").
and return all the services apis responses them as a one response with the same unified data.

## Running the code

### 1. Create a python virtual environment
`virtualenv -p /usr/bin/python3.8 venv`

### 2. Move to the python virtual environment
`source venv/bin/activate`

### 3. Rename .env_example to .env and add the environment variables in it.
`mv .env_example .env`

### 4. Install the project requirements:
`pip install -r requirements.txt`

### 5. Run the project:
`uvicorn main:app --reload`

# Tests 
### for running the tests, run:
`pytest`

# extra info
### To check the requests endpoints in the browser and interact with them head to:
- http://127.0.0.1:8000/docs

Thanks for The Code Review.

~ Ameen Alakahras