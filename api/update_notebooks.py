import os
import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
from .amazon_api import AmazonAPI

app = Flask(__name__)

@app.route("/api/update_notebooks", methods=["POST"])
def update_notebooks():
    # 1. Conectar ao Supabase
    try:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")
        supabase: Client = create_client(url, key)
    except Exception as e:
        return jsonify({"error": "Falha ao conectar ao Supabase", "details": str(e)}), 500

    # 2. Ler o ASIN enviado na requisição
    try:
        data = request.get_json()
        asin = data.get("asin")
        if not asin:
            raise ValueError("ASIN não fornecido no corpo da requisição")
    except Exception as e:
        return jsonify({"error": "Requisição inválida", "details": str(e)}), 400

    # 3. Chamar a API da Amazon para buscar dados do ASIN
    try:
        amazon_api = AmazonAPI()
        dados_da_amazon = amazon_api.get_item_info(asin)
        
        if not dados_da_amazon:
            return jsonify({"error": f"Produto com ASIN {asin} não encontrado na Amazon"}), 404
            
    except Exception as e:
        return jsonify({"error": "Falha ao buscar dados da Amazon", "details": str(e)}), 500

    # 4. Inserir/Atualizar os dados no Supabase
    try:
        data, count = supabase.table("notebooks").upsert({
            "asin": asin,
            "nome_curto": " ".join(dados_da_amazon.get("titulo_amazon", "").split()[0:3]),
            "memoria_ram": _extract_ram_from_features(dados_da_amazon.get("caracteristicas", [])),
            **dados_da_amazon
        }).execute()

    except Exception as e:
        return jsonify({"error": "Falha ao salvar dados no Supabase", "details": str(e)}), 500

    # 5. Enviar resposta de sucesso
    return jsonify({"message": f"Notebook com ASIN {asin} processado com sucesso!", "data": dados_da_amazon}), 200

def _extract_ram_from_features(features):
    for feature in features:
        if 'GB' in feature and ('RAM' in feature.upper() or 'MEMORY' in feature.upper()):
            import re
            match = re.search(r'(\d+)\s*GB', feature)
            if match:
                return int(match.group(1))
    return 8



