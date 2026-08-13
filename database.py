import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json


JSON_FILE = "pets.json"

INICIATIVA_INFO = {
    "nome": "Adoção de Pets Salvador",
    "cidade": "Salvador - BA",
    "chave_pix": "adocaodepetsssa@gmail.com",
    "tipo_chave": "E-mail",
    "titular": "Iniciativa Resgate e Adoção",
    "whatsapp": "7191096096"
}

# Carrega as informações fixas (WhatsApp, Pix, etc.) do arquivo JSON
def obter_info_iniciativa():
    try:
        with open("pets.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            
            # Se o JSON for uma Lista, procuramos o dicionário que contém a chave "info"
            if isinstance(dados, list):
                for item in dados:
                    if isinstance(item, dict) and "info" in item:
                        return item["info"]
                return {} # Se não achar a chave "info" na lista
                
            # Se o JSON já for um Dicionário principal
            elif isinstance(dados, dict):
                return dados.get("info", {})
                
            return {}
    except Exception as e:
        print(f"Erro ao ler informações da ONG: {e}")
        return {}
def obter_animais_por_especie(especie: str):
    db = SessionLocal()
    try:
        # Busca no banco de dados Supabase filtrando pela espécie
        return db.query(PetModel).filter(PetModel.especie.ilike(especie)).all()
    finally:
        db.close()

load_dotenv()

# Pega a URL do banco do arquivo .env ou do Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Correção caso a URL venha como 'postgres://' (SQLAlchemy exige 'postgresql://')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Modelo da tabela de Pets
class PetModel(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    especie = Column(String, nullable=False)
    idade = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    foto = Column(
        String, nullable=False
    )  # Aqui vai salvar a URL do Cloudinary!


# Cria as tabelas no Supabase se elas não existirem
def init_db():
    Base.metadata.create_all(bind=engine)


# Funções de leitura e escrita
def obter_pets():
    db = SessionLocal()
    try:
        return db.query(PetModel).all()
    finally:
        db.close()


def salvar_pet(
    nome: str, especie: str, idade: str, descricao: str, foto_url: str
):
    db = SessionLocal()
    try:
        novo_pet = PetModel(
            nome=nome,
            especie=especie,
            idade=idade,
            descricao=descricao,
            foto=foto_url,
        )
        db.add(novo_pet)
        db.commit()
        db.refresh(novo_pet)
        return novo_pet
    finally:
        db.close()