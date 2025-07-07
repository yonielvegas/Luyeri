from fastapi import FastAPI
from routes.routes import login_router

app = FastAPI()

# Incluir el router de temperatura_router con la etiqueta 'Conversiones de Temperaturas'
app.include_router(login_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
