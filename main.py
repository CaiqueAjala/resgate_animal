import shutil
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SENHA_ADMIN = "CAUANnani@94"  

# ----------------------------------------------------
# ROTAS PÚBLICAS
# ----------------------------------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"info": database.obter_info_iniciativa()}
    )
#Rota de doação dos animais
@app.get("/animais/{especie}")
def listar_animais(request: Request, especie: str):
    tipo_map = {"cachorros": "cachorro", "gatos": "gato"}
    especie_filtrada = tipo_map.get(especie, "cachorro")
    pet_list = database.obter_animais_por_especie(especie_filtrada)
    
    return templates.TemplateResponse(
        request=request, 
        name="animais.html", 
        context={
            "pet_list": pet_list, 
            "tipo": especie.capitalize(),
            "info": database.obter_info_iniciativa()
        }
    )

#Doação Pix
@app.get("/doar")
def pagina_doacao(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="doar.html",
    context={"info": database.obter_info_iniciativa}

    )
# ----------------------------------------------------
# ROTAS DE ADMINISTRAÇÃO
# ----------------------------------------------------

# 1. Página de Login
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin_login.html")

# 2. Processamento do Login
@app.post("/admin/login")
def admin_login(senha: str = Form(...)):
    if senha == SENHA_ADMIN:
        response = RedirectResponse(url="/admin/painel", status_code=303)
        # Salva um Cookie no navegador indicando que ele está logado
        response.set_cookie(key="admin_access", value="logged_in")
        return response
    
    return RedirectResponse(url="/admin/login?erro=1", status_code=303)

# 3. Painel Administrativo (Protegido por Cookie)
@app.get("/admin/painel", response_class=HTMLResponse)
def admin_painel(request: Request, admin_access: str = Cookie(None)):
    # Validação: Se não tiver o cookie correto, redireciona pro login
    if admin_access != "logged_in":
        return RedirectResponse(url="/admin/login", status_code=303)
        
    pets = database.carregar_pets()
    # ✅ Forma correta:
    return templates.TemplateResponse(
        request=request, 
        name="admin_painel.html", 
        context={"pets": pets}
    )
# 4. Rota para Cadastrar Novo Pet
@app.post("/admin/cadastrar")
async def cadastrar_pet(
    nome: str = Form(...),
    especie: str = Form(...),
    raca: str = Form("SRD"),
    idade: str = Form(...),
    porte: str = Form(...),
    descricao: str = Form(...),
    foto: UploadFile = File(...),
    admin_access: str = Cookie(None)
):
    if admin_access != "logged_in":
        return RedirectResponse(url="/admin/login", status_code=303)

    # 1. Salva o arquivo da foto na pasta static/img/
    caminho_foto_local = f"static/img/{foto.filename}"
    with open(caminho_foto_local, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # 2. Prepara o dicionário do novo pet
    novo_pet = {
        "nome": nome,
        "especie": especie,
        "raca": raca,
        "idade": idade,
        "porte": porte,
        "descricao": descricao,
        "fotos": [f"/static/img/{foto.filename}"]
    }

    # 3. Salva no JSON através do database.py
    database.adicionar_novo_pet(novo_pet)

    return RedirectResponse(url="/admin/painel", status_code=303)

# 5. Rota para Sair/Logout
@app.get("/admin/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_access")
    return response