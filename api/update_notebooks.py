import os
import json
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client
from .amazon_api import AmazonAPI

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Conectar ao Supabase
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_SERVICE_KEY")
            supabase: Client = create_client(url, key)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao conectar ao Supabase", "details": str(e)}).encode('utf-8'))
            return

        # 2. Ler o ASIN enviado na requisição
        try:
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            asin = body.get("asin")
            if not asin:
                raise ValueError("ASIN não fornecido no corpo da requisição")
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Requisição inválida", "details": str(e)}).encode('utf-8'))
            return

        # 3. Chamar a API da Amazon para buscar dados do ASIN
        try:
            amazon_api = AmazonAPI()
            dados_da_amazon = amazon_api.get_item_info(asin)
            
            if not dados_da_amazon:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Produto com ASIN {asin} não encontrado na Amazon"}).encode('utf-8'))
                return
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao buscar dados da Amazon", "details": str(e)}).encode('utf-8'))
            return

        # 4. Inserir/Atualizar os dados no Supabase
        try:
            data, count = supabase.table("notebooks").upsert({
                "asin": asin,
                "nome_curto": " ".join(dados_da_amazon.get("titulo_amazon", "").split()[0:3]),
                "memoria_ram": self._extract_ram_from_features(dados_da_amazon.get("caracteristicas", [])),
                **dados_da_amazon
            }).execute()

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao salvar dados no Supabase", "details": str(e)}).encode('utf-8'))
            return

        # 5. Enviar resposta de sucesso
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"Notebook com ASIN {asin} processado com sucesso!", "data": dados_da_amazon}).encode('utf-8'))
        return

    def _extract_ram_from_features(self, features):
        for feature in features:
            if 'GB' in feature and ('RAM' in feature.upper() or 'MEMORY' in feature.upper()):
                import re
                match = re.search(r'(\d+)\s*GB', feature)
                if match:
                    return int(match.group(1))
        return 8


