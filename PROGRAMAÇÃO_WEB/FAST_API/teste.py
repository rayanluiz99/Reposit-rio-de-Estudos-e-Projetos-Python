from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {'mensagem': 'Home'}


@app.get("/cadastro")
def root():
    return {'mensagem': 'Cadastro'}


@app.get("/login")
def root():
    return {'mensagem': 'Login'}