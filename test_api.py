#!/usr/bin/env python3
"""
Script de teste para a API de notebooks
"""
import json
import os
from amazon_api import AmazonAPI

def test_amazon_api():
    """
    Testa a integração com a Amazon PAAPI 5.0
    """
    print("=== Teste da Amazon API ===")
    
    # Verificar se as variáveis de ambiente estão definidas
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_ASSOCIATE_TAG']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("Configure as variáveis de ambiente antes de executar o teste.")
        return False
    
    try:
        # Inicializar a API
        api = AmazonAPI()
        print("✅ Amazon API inicializada com sucesso")
        
        # Testar com um ASIN de exemplo (MacBook Air)
        test_asin = "B08N5WRWNW"  # ASIN de exemplo
        print(f"🔍 Testando busca para ASIN: {test_asin}")
        
        result = api.get_item_info(test_asin)
        
        if result:
            print("✅ Produto encontrado!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print("❌ Produto não encontrado ou erro na API")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

def test_supabase_connection():
    """
    Testa a conexão com o Supabase
    """
    print("\n=== Teste da Conexão Supabase ===")
    
    try:
        from supabase import create_client, Client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            print("❌ Variáveis SUPABASE_URL ou SUPABASE_SERVICE_KEY não configuradas")
            return False
        
        supabase = create_client(url, key)
        
        # Testar uma consulta simples
        response = supabase.table("notebooks").select("*").limit(1).execute()
        print("✅ Conexão com Supabase estabelecida com sucesso")
        print(f"📊 Tabela 'notebooks' acessível (registros encontrados: {len(response.data)})")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes da API de Notebooks\n")
    
    # Teste 1: Amazon API
    amazon_ok = test_amazon_api()
    
    # Teste 2: Supabase
    supabase_ok = test_supabase_connection()
    
    print("\n=== Resumo dos Testes ===")
    print(f"Amazon API: {'✅ OK' if amazon_ok else '❌ FALHOU'}")
    print(f"Supabase: {'✅ OK' if supabase_ok else '❌ FALHOU'}")
    
    if amazon_ok and supabase_ok:
        print("\n🎉 Todos os testes passaram! A API está pronta para uso.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique a configuração antes de fazer o deploy.")

