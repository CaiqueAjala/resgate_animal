import time
import requests

URL_DO_SITE = "https://resgate-animal.onrender.com"

print("Iniciando o bot de mantimento ativo...")

while True:
    try:
        # Faz uma requisição GET na sua API
        resposta = requests.get(URL_DO_SITE)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping enviado com sucesso! Status: {resposta.status_code}")
    except Exception as e:
        print(f"Erro ao tentar acessar o site: {e}")

    # Espera 10 minutos (600 segundos) antes de fazer o próximo ping
    # 10 minutos * 60 segundos = 600 segundos
    time.sleep(600)

