import urllib.request
import urllib.error

URL_DO_SITE = "https://resgate-animal.onrender.com"

try:
    # Adicionamos um timeout de 10 segundos para não ficar travado para sempre
    with urllib.request.urlopen(URL_DO_SITE, timeout=10) as resposta:
        print(f"Ping enviado com sucesso! Status: {resposta.status}")
except Exception as e:
    print(f"Erro ao tentar acessar o site: {e}")