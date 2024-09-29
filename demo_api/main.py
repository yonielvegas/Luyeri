from fastapi import FastAPI
from routes.routes import temperatura_router

app = FastAPI()

# Incluir el router de temperatura_router con la etiqueta 'Conversiones de Temperaturas'
app.include_router(temperatura_router, tags=["Conversiones de Temperaturas"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)