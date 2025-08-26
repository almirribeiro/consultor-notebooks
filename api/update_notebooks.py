from http.server import BaseHTTPRequestHandler
import os
import json
from supabase import create_client, Client

# Função principal que a Vercel vai executar
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Conectar ao Supabase
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_SERVICE_KEY")
            supabase: Client = create_client(url, key)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao conectar ao Supabase", "details": str(e)}).encode())
            return

        # 2. Ler o ASIN enviado na requisição
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data)
            asin = body.get("asin")
            if not asin:
                raise ValueError("ASIN não fornecido no corpo da requisição")
        except Exception as e:
            self.send_response(400) # Bad Request
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Requisição inválida", "details": str(e)}).encode())
            return

        # 3. (FUTURO) Chamar a API da Amazon para buscar dados do ASIN
        # Por enquanto, vamos simular os dados para testar o fluxo
        dados_simulados_da_amazon = {
            "titulo_amazon": f"Notebook Simulado para ASIN {asin}",
            "preco_atual": 4999.99,
            "link_afiliado": f"https://www.amazon.com.br/dp/{asin}?tag={os.environ.get("AMAZON_AFFILIATE_TAG")}",
            "url_imagem": "https://via.placeholder.com/150",
            "disponivel": True
        }

        # 4. Inserir/Atualizar os dados no Supabase
        try:
            # Tenta atualizar um notebook existente com o mesmo ASIN
            # Se não existir, insere um novo (upsert=True)
            data, count = supabase.table("notebooks").upsert({
                "asin": asin,
                "nome_curto": f"Notebook {asin}", # Provisório
                "memoria_ram": 16, # Provisório
                **dados_simulados_da_amazon
            }).execute()

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao salvar dados no Supabase", "details": str(e)}).encode())
            return

        # 5. Enviar resposta de sucesso
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": f"Notebook com ASIN {asin} processado com sucesso!", "data": dados_simulados_da_amazon}
        self.wfile.write(json.dumps(response).encode())
        return

