import os
import json
from supabase import create_client, Client
from amazon_api import AmazonAPI

def handler(request, response):
    # 1. Conectar ao Supabase
    try:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")
        supabase: Client = create_client(url, key)
    except Exception as e:
        response.status = 500
        response.json({"error": "Falha ao conectar ao Supabase", "details": str(e)})
        return

    # 2. Ler o ASIN enviado na requisição
    try:
        body = json.loads(request.body)
        asin = body.get("asin")
        if not asin:
            raise ValueError("ASIN não fornecido no corpo da requisição")
    except Exception as e:
        response.status = 400 # Bad Request
        response.json({"error": "Requisição inválida", "details": str(e)})
        return

    # 3. Chamar a API da Amazon para buscar dados do ASIN
    try:
        amazon_api = AmazonAPI()
        dados_da_amazon = amazon_api.get_item_info(asin)
        
        if not dados_da_amazon:
            response.status = 404
            response.json({"error": f"Produto com ASIN {asin} não encontrado na Amazon"})
            return
            
    except Exception as e:
        response.status = 500
        response.json({"error": "Falha ao buscar dados da Amazon", "details": str(e)})
        return

    # 4. Inserir/Atualizar os dados no Supabase
    try:
        # Tenta atualizar um notebook existente com o mesmo ASIN
        # Se não existir, insere um novo (upsert=True)
        data, count = supabase.table("notebooks").upsert({
            "asin": asin,
            "nome_curto": " ".join(dados_da_amazon.get("titulo_amazon", "").split()[0:3]),  # Primeiras 3 palavras como nome curto
            "memoria_ram": _extract_ram_from_features(dados_da_amazon.get("caracteristicas", [])),
            **dados_da_amazon
        }).execute()

    except Exception as e:
        response.status = 500
        response.json({"error": "Falha ao salvar dados no Supabase", "details": str(e)})
        return

    # 5. Enviar resposta de sucesso
    response.status = 200
    response.json({"message": f"Notebook com ASIN {asin} processado com sucesso!", "data": dados_da_amazon})
    return

def _extract_ram_from_features(features):
    """
    Extrai informação de RAM das características do produto
    """
    for feature in features:
        if 'GB' in feature and ('RAM' in feature.upper() or 'MEMORY' in feature.upper()):
            import re
            match = re.search(r'(\d+)\s*GB', feature)
            if match:
                return int(match.group(1))
    return 8  # Valor padrão se não encontrar


