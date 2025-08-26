import os
import json
import hmac
import hashlib
import base64
import datetime
import requests
from urllib.parse import quote_plus, urlencode
from lxml import etree

class AmazonAPI:
    def __init__(self):
        self.access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.associate_tag = os.environ.get('AWS_ASSOCIATE_TAG')
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Endpoint da PAAPI 5.0
        if self.region == 'us-east-1':
            self.endpoint = 'webservices.amazon.com'
        elif self.region == 'us-west-2':
            self.endpoint = 'webservices.amazon.com'
        elif self.region == 'eu-west-1':
            self.endpoint = 'webservices.amazon.co.uk'
        else:
            self.endpoint = 'webservices.amazon.com'
    
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
                "Marketplace": "www.amazon.com.br"
            }
            
            # Headers necessários para a PAAPI 5.0
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems',
                'Content-Encoding': 'amz-1.0'
            }
            
            # Criar assinatura AWS4
            signed_headers = self._sign_request(
                method='POST',
                uri='/paapi5/getitems',
                payload=json.dumps(payload),
                headers=headers
            )
            
            # Fazer a requisição
            url = f'https://{self.endpoint}/paapi5/getitems'
            response = requests.post(url, data=json.dumps(payload), headers=signed_headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_item_response(data)
            else:
                print(f"Erro na API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao buscar item: {str(e)}")
            return None
    
    def _sign_request(self, method, uri, payload, headers):
        """
        Cria a assinatura AWS4 para autenticação
        """
        # Timestamp
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = t.strftime('%Y%m%d')
        
        # Canonical request
        canonical_uri = uri
        canonical_querystring = ''
        canonical_headers = f'host:{self.endpoint}\nx-amz-date:{amz_date}\n'
        signed_headers_list = 'host;x-amz-date'
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers_list}\n{payload_hash}'
        
        # String to sign
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f'{date_stamp}/{self.region}/execute-api/aws4_request'
        string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
        
        # Signing key
        signing_key = self._get_signature_key(self.secret_key, date_stamp, self.region, 'execute-api')
        
        # Signature
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Authorization header
        authorization_header = f'{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers_list}, Signature={signature}'
        
        # Add auth headers
        headers['X-Amz-Date'] = amz_date
        headers['Authorization'] = authorization_header
        
        return headers
    
    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        """
        Gera a chave de assinatura AWS4
        """
        k_date = hmac.new(('AWS4' + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
        return k_signing
    
    def _parse_item_response(self, data):
        """
        Extrai informações relevantes da resposta da API
        """
        try:
            if 'ItemsResult' not in data or 'Items' not in data['ItemsResult']:
                return None
            
            item = data['ItemsResult']['Items'][0]
            
            # Extrair informações básicas
            title = item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', 'N/A')
            
            # Preço
            price = 'N/A'
            if 'Offers' in item and 'Listings' in item['Offers']:
                listings = item['Offers']['Listings']
                if listings and 'Price' in listings[0]:
                    price_info = listings[0]['Price']
                    if 'DisplayAmount' in price_info:
                        price = price_info['DisplayAmount']
            
            # Imagem
            image_url = 'N/A'
            if 'Images' in item and 'Primary' in item['Images']:
                image_url = item['Images']['Primary']['Large']['URL']
            
            # URL do produto
            detail_url = item.get('DetailPageURL', 'N/A')
            
            # Features/características
            features = []
            if 'ItemInfo' in item and 'Features' in item['ItemInfo']:
                features = [f.get('DisplayValue', '') for f in item['ItemInfo']['Features'].get('DisplayValues', [])]
            
            return {
                'titulo_amazon': title,
                'preco_atual': price,
                'link_afiliado': detail_url,
                'url_imagem': image_url,
                'disponivel': True,
                'caracteristicas': features
            }
            
        except Exception as e:
            print(f"Erro ao processar resposta: {str(e)}")
            return None

