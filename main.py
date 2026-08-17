import shutil
import os
from fastapi import FastAPI, Request, Form, File, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cloudinary
import cloudinary.uploader
from database import init_db, obter_pets, salvar_pet,obter_animais_por_especie, obter_info_iniciativa



# Configura o Cloudinary com as chaves do .env
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)



app = FastAPI()
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD", "senha_temporaria_123")

# Inicializa o banco ao subir a aplicação
@app.on_event("startup")
def startup():
    init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------
# ROTAS PÚBLICAS
# ----------------------------------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"info": obter_info_iniciativa()}
    )
#Rota de doação dos animais
@app.get("/animais/{especie}")
def listar_animais(request: Request, especie: str):
    tipo_map = {"cachorros": "cachorro", "gatos": "gato"}
    especie_filtrada = tipo_map.get(especie, "cachorro")
    
    # Chama a função direto sem a palavra "database." na frente
    pet_list = obter_animais_por_especie(especie_filtrada)

    return templates.TemplateResponse(
        request=request,
        name="animais.html",
        context={"request": request, "pets": pet_list, "info": obter_info_iniciativa()}
    )

#Doação Pix
@app.get("/doar")
def pagina_doacao(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="doar.html",
    context={"info": obter_info_iniciativa()}

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
# 3. Painel Administrativo (Protegido por Cookie)
@app.get("/admin/painel", response_class=HTMLResponse)
def admin_painel(request: Request, admin_access: str = Cookie(None)):
    # Validação: Se não tiver o cookie correto, redireciona pro login
    if admin_access != "logged_in":
        return RedirectResponse(url="/admin/login", status_code=303)
    
    # 🔍 Busca todos os pets cadastrados direto do Banco de Dados (Supabase)
    pets = obter_pets()

    # Retorna o template passando a lista 'pets' que acabamos de buscar
    return templates.TemplateResponse(
        request=request,
        name="admin_painel.html",
        context={"request": request, "pets": pets}
    )
# 4. Rota para Cadastrar Novo Pet
@app.post("/admin/adicionar")
async def adicionar_pet(
    nome: str = Form(...),
    especie: str = Form(...),
    idade: str = Form(...),
    descricao: str = Form(...),
    foto: UploadFile = File(...),
    admin_access: str = Cookie(None)
):
    if admin_access != "logged_in":
        return RedirectResponse(url="/admin/login", status_code=303)

# 5. Rota para Sair/Logout
@app.get("/admin/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_access")
    return response