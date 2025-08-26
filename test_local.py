#!/usr/bin/env python3
"""
Teste local simulado da API (sem credenciais reais)
"""
import json
import sys
import os

# Adicionar o diretório api ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

def test_api_structure():
    """
    Testa se a estrutura da API está correta
    """
    print("=== Teste da Estrutura da API ===")
    
    try:
        # Testar importação dos módulos
        from amazon_api import AmazonAPI
        print("✅ Módulo amazon_api importado com sucesso")
        
        # Testar se a classe pode ser instanciada (mesmo sem credenciais)
        try:
            api = AmazonAPI()
            print("✅ Classe AmazonAPI instanciada")
        except Exception as e:
            print(f"⚠️  AmazonAPI instanciada com aviso: {str(e)}")
        
        # Testar importação do handler
        from update_notebooks import handler
        print("✅ Handler update_notebooks importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def test_api_methods():
    """
    Testa os métodos da API (estrutura)
    """
    print("\n=== Teste dos Métodos da API ===")
    
    try:
        from amazon_api import AmazonAPI
        
        api = AmazonAPI()
        
        # Verificar se os métodos existem
        methods = ['get_item_info', '_sign_request', '_get_signature_key', '_parse_item_response']
        
        for method in methods:
            if hasattr(api, method):
                print(f"✅ Método {method} encontrado")
            else:
                print(f"❌ Método {method} não encontrado")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar métodos: {str(e)}")
        return False

def simulate_api_response():
    """
    Simula uma resposta da API para testar o processamento
    """
    print("\n=== Simulação de Resposta da API ===")
    
    try:
        from amazon_api import AmazonAPI
        
        api = AmazonAPI()
        
        # Dados simulados de resposta da Amazon PAAPI 5.0
        mock_response = {
            "ItemsResult": {
                "Items": [{
                    "ItemInfo": {
                        "Title": {
                            "DisplayValue": "Notebook Dell Inspiron 15 3000"
                        },
                        "Features": {
                            "DisplayValues": [
                                {"DisplayValue": "Intel Core i5 Processor"},
                                {"DisplayValue": "8GB RAM Memory"},
                                {"DisplayValue": "256GB SSD Storage"},
                                {"DisplayValue": "15.6 inch Full HD Display"}
                            ]
                        }
                    },
                    "Offers": {
                        "Listings": [{
                            "Price": {
                                "DisplayAmount": "R$ 2.499,99"
                            }
                        }]
                    },
                    "Images": {
                        "Primary": {
                            "Large": {
                                "URL": "https://example.com/notebook-image.jpg"
                            }
                        }
                    },
                    "DetailPageURL": "https://www.amazon.com.br/dp/B08N5WRWNW"
                }]
            }
        }
        
        # Testar o método de parsing
        result = api._parse_item_response(mock_response)
        
        if result:
            print("✅ Processamento de resposta simulada bem-sucedido")
            print("📊 Dados extraídos:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print("❌ Falha no processamento da resposta simulada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na simulação: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando testes locais da API (modo simulado)\n")
    
    # Teste 1: Estrutura da API
    structure_ok = test_api_structure()
    
    # Teste 2: Métodos da API
    methods_ok = test_api_methods()
    
    # Teste 3: Simulação de resposta
    simulation_ok = simulate_api_response()
    
    print("\n=== Resumo dos Testes Locais ===")
    print(f"Estrutura da API: {'✅ OK' if structure_ok else '❌ FALHOU'}")
    print(f"Métodos da API: {'✅ OK' if methods_ok else '❌ FALHOU'}")
    print(f"Simulação de resposta: {'✅ OK' if simulation_ok else '❌ FALHOU'}")
    
    if structure_ok and methods_ok and simulation_ok:
        print("\n🎉 Todos os testes locais passaram!")
        print("📝 A API está estruturalmente correta e pronta para receber credenciais reais.")
        print("🚀 Próximo passo: Configurar as variáveis de ambiente no Vercel e fazer o deploy.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique o código antes de prosseguir.")

