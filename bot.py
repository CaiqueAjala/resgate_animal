import urllib.request
import urllib.error

# URL do seu site no Render
URL_DO_SITE = "https://resgate-animal.onrender.com"

try:
    # Faz a requisição usando o urllib nativo
    with urllib.request.urlopen(URL_DO_SITE) as resposta:
        print(f"Ping enviado com sucesso! Status: {resposta.status}")
except Exception as e:
    print(f"Erro ao tentar acessar o site: {e}")