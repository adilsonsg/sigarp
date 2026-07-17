from fastapi import FastAPI


app = FastAPI(
    title="SIGARP API",
    version="0.1.0",
    description="Sistema Inteligente de Gestão e Análise de Registro de Preços"
)


@app.get("/health")
def health():

    return {
        "application": "SIGARP",
        "version": "0.1.0",
        "status": "online"
    }
