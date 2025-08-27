import os
import json
import datetime
import requests
from lxml import etree
import boto3
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth
from botocore.exceptions import ClientError

class AmazonAPI:
    def __init__(self):
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.associate_tag = os.environ.get("AWS_ASSOCIATE_TAG")
        self.region = os.environ.get("AWS_REGION", "sa-east-1") # Definindo a região padrão como sa-east-1
        
        # Endpoint da PAAPI 5.0
        if self.region == "sa-east-1":
            self.endpoint = "webservices.amazon.com.br"
        elif self.region == "us-east-1":
            self.endpoint = "webservices.amazon.com"
        elif self.region == "us-west-2":
            self.endpoint = "webservices.amazon.com"
        elif self.region == "eu-west-1":
            self.endpoint = "webservices.amazon.co.uk"
        else:
            self.endpoint = "webservices.amazon.com"

        self.service = "ProductAdvertisingAPI"
        self.host = self.endpoint
    
    def get_item_info(self, asin):
        """
        Busca informações de um produto específico usando o ASIN
        """
        try:
            # Payload para a PAAPI 5.0
            payload = {
                "ItemIds": [asin],
                "Resources": [
                    "ItemInfo.Title",
                    "ItemInfo.Features",
                    "ItemInfo.ProductInfo",
                    "Offers.Listings.Price",
                    "Images.Primary.Large",
                    "ItemInfo.TechnicalInfo"
                ],
                "PartnerTag": self.associate_tag,
                "PartnerType": "Associates",
                "Marketplace": "www.amazon.com.br" # Definindo o Marketplace explicitamente para o Brasil
            }
            
            # Headers necessários para a PAAPI 5.0
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems",
                "Content-Encoding": "amz-1.0"
            }
            
            # Criar e assinar a requisição usando boto3
            request_url = f"https://{self.endpoint}/paapi5/getitems"
            request = AWSRequest(method="POST", url=request_url, data=json.dumps(payload), headers=headers)
            
            # Usar uma sessão boto3 para obter as credenciais
            session = boto3.Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
            credentials = session.get_credentials()
            
            SigV4Auth(credentials, self.service, self.region).add_auth(request)
            
            # Fazer a requisição
            response = requests.post(request.url, headers=request.headers, data=request.body)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_item_response(data)
            else:
                print(f"Erro na API: {response.status_code} - {response.text}")
                return None
                
        except ClientError as e:
            print(f"Erro do cliente AWS: {e}")
            return None
        except Exception as e:
            print(f"Erro ao buscar item: {str(e)}")
            return None
    
    def _parse_item_response(self, data):
        """
        Extrai informações relevantes da resposta da API
        """
        try:
            if "ItemsResult" not in data or "Items" not in data["ItemsResult"]:
                # Adicionado tratamento para TooManyRequestsException
                if "Errors" in data and any("TooManyRequests" in error.get("Code", "") for error in data["Errors"]):
                    print("Erro: Limite de requisições excedido para a Amazon PAAPI5.")
                    return None
                return None
            
            item = data["ItemsResult"]["Items"][0]
            
            # Extrair informações básicas
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "N/A")
            
            # Preço
            price = "N/A"
            if "Offers" in item and "Listings" in item["Offers"]:
                listings = item["Offers"]["Listings"]
                if listings and "Price" in listings[0]:
                    price_info = listings[0]["Price"]
                    if "DisplayAmount" in price_info:
                        price = price_info["DisplayAmount"]
            
            # Imagem
            image_url = "N/A"
            if "Images" in item and "Primary" in item["Images"]:
                image_url = item["Images"]["Primary"]["Large"]["URL"]
            
            # URL do produto
            detail_url = item.get("DetailPageURL", "N/A")
            
            # Features/características
            features = []
            if "ItemInfo" in item and "Features" in item["ItemInfo"]:
                features = [f.get("DisplayValue", "") for f in item["ItemInfo"]["Features"].get("DisplayValues", [])]
            
            return {
                "titulo_amazon": title,
                "preco_atual": price,
                "link_afiliado": detail_url,
                "url_imagem": image_url,
                "disponivel": True,
                "caracteristicas": features
            }
            
        except Exception as e:
            print(f"Erro ao processar resposta: {str(e)}")
            return None



