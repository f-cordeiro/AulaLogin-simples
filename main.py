# Criar um sistema SSR

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Usuario

app = FastAPI(title="Sistema de login simples")

#Roda o código
# python -m uvicorn main:app --reload

templates = Jinja2Templates(directory="templates")

@app.get("/")
def tela_inicial(request: Request):
    return templates.TemplateResponse(
        request,
        "main.html",
        {"request": request}
    )

@app.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request,
        "cadastro.html",
        {"request": request}
    )

@app.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request}
    )

# POST - CRIARUM USUARIO
@app.post("/cadastro")
def cadastrar_usuario(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    
    #Procurar o email no banco de dados.
    user_existente = db.query(Usuario).filter_by(email=email).first()
    # user_existente = db.query(Usuario).filter(Usuario.email == email).first()

    if user_existente:
        return templates.TemplateResponse(
            request,
            "cadastro.html",
            {"request": request, "erro": "Email já cadastrado."}
        )
    
    #Cria um objeto
    novo_usuario = Usuario(email=email, senha=senha)
    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)


@app.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    

    #Verificar login
    usuario = db.query(Usuario).filter(Usuario.email == email).filter(Usuario.senha == senha).first()
    # id, email, senha

    if usuario is None:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "erro": "Email ou senha inválidos. "}
        )
    
    response = RedirectResponse(url="/poslogin", status_code=303)

    #criando o cookie simples
    response.set_cookie(
        key="usuario_id",
        value=str(usuario.id)
    )

    return response

#Tela protegida
@app.get("/poslogin")
def tela_poslogin(request: Request, db: Session = Depends(get_db)):

    #Verificar id no cookie
    usuario_id = request.cookies.get("usuario_id")

    if usuario_id is None:
        return RedirectResponse(url="/login", status_code=303)
    
    user_existente = db.query(Usuario).get(int(usuario_id))

    return templates.TemplateResponse(
        request,
        "inicio.html",
        {"request": request, "usuario": user_existente}
    )

