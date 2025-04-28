import uvicorn

if __name__ == "__main__":
    print("Starting Report Generator microservice...")
    print("API documentation will be available at http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
