from http.server import BaseHTTPRequestHandler
import os
import json
from supabase import create_client, Client
from amazon_api import AmazonAPI

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

        # 3. Chamar a API da Amazon para buscar dados do ASIN
        try:
            amazon_api = AmazonAPI()
            dados_da_amazon = amazon_api.get_item_info(asin)
            
            if not dados_da_amazon:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Produto com ASIN {asin} não encontrado na Amazon"}).encode())
                return
                
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Falha ao buscar dados da Amazon", "details": str(e)}).encode())
            return

        # 4. Inserir/Atualizar os dados no Supabase
        try:
            # Tenta atualizar um notebook existente com o mesmo ASIN
            # Se não existir, insere um novo (upsert=True)
            data, count = supabase.table("notebooks").upsert({
                "asin": asin,
                "nome_curto": dados_da_amazon.get("titulo_amazon", "").split()[0:3],  # Primeiras 3 palavras como nome curto
                "memoria_ram": self._extract_ram_from_features(dados_da_amazon.get("caracteristicas", [])),
                **dados_da_amazon
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
        response = {"message": f"Notebook com ASIN {asin} processado com sucesso!", "data": dados_da_amazon}
        self.wfile.write(json.dumps(response).encode())
        return

    def _extract_ram_from_features(self, features):
        """
        Extrai informação de RAM das características do produto
        """
        for feature in features:
            if 'GB' in feature and ('RAM' in feature.upper() or 'Memory' in feature):
                # Tenta extrair o número de GB
                import re
                match = re.search(r'(\d+)\s*GB', feature)
                if match:
                    return int(match.group(1))
        return 8  # Valor padrão se não encontrar

