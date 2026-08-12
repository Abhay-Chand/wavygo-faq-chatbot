from fastapi import FastAPI

app = FastAPI(title="WavyGo FAQ Chatbot")


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "WavyGo FAQ Chatbot"
    }