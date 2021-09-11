from fastapi import FastAPI, Depends

app = FastAPI()


@app.get("/news")
def list_news():
    return {"Hello": "World"}


@app.get("/news?query={query}")
def search_news(query: str):
    return {"Hello": "World"}
