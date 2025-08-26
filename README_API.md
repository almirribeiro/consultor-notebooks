# API de Recomendação de Notebooks

## Visão Geral

Esta API integra com a Amazon Product Advertising API (PAAPI 5.0) para buscar informações detalhadas de notebooks e armazenar no Supabase.

## Funcionalidades

- ✅ Integração completa com Amazon PAAPI 5.0
- ✅ Autenticação AWS4 para requisições seguras
- ✅ Extração automática de especificações (RAM, processador, etc.)
- ✅ Armazenamento no Supabase com upsert automático
- ✅ Tratamento de erros robusto
- ✅ Compatível com Vercel Functions

## Endpoint

### POST `/api/update_notebooks`

Busca informações de um notebook na Amazon e salva no Supabase.

**Corpo da Requisição:**
```json
{
    "asin": "B08N5WRWNW"
}
```

**Resposta de Sucesso (200):**
```json
{
    "message": "Notebook com ASIN B08N5WRWNW processado com sucesso!",
    "data": {
        "titulo_amazon": "Notebook Dell Inspiron 15 3000",
        "preco_atual": "R$ 2.499,99",
        "link_afiliado": "https://www.amazon.com.br/dp/B08N5WRWNW",
        "url_imagem": "https://example.com/image.jpg",
        "disponivel": true,
        "caracteristicas": ["Intel Core i5", "8GB RAM", "256GB SSD"]
    }
}
```

**Resposta de Erro (404):**
```json
{
    "error": "Produto com ASIN B08N5WRWNW não encontrado na Amazon"
}
```

## Configuração

### Variáveis de Ambiente Necessárias

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Amazon PAAPI 5.0
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ASSOCIATE_TAG=your_associate_tag
AWS_REGION=us-east-1
```

### Estrutura da Tabela Supabase

```sql
CREATE TABLE notebooks (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) UNIQUE NOT NULL,
    nome_curto VARCHAR(255),
    memoria_ram INTEGER,
    titulo_amazon TEXT,
    preco_atual VARCHAR(50),
    link_afiliado TEXT,
    url_imagem TEXT,
    disponivel BOOLEAN DEFAULT true,
    caracteristicas TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Deploy no Vercel

1. **Conectar repositório**: Conecte seu repositório GitHub ao Vercel
2. **Configurar variáveis**: Adicione as variáveis de ambiente no painel do Vercel
3. **Deploy automático**: O Vercel detectará automaticamente a função Python

## Testes

Execute os testes locais:
```bash
python test_local.py  # Testes estruturais (sem credenciais)
python test_api.py    # Testes completos (com credenciais)
```

## Arquitetura

```
Frontend (Next.js) → Vercel Function (Python) → Amazon PAAPI 5.0
                                              ↓
                                         Supabase Database
```

## Limitações da PAAPI 5.0

- **Rate Limits**: 1 requisição por segundo por padrão
- **Quota**: 8.640 requisições por dia (pode variar)
- **Aprovação**: Requer aprovação da Amazon para uso em produção

## Troubleshooting

### Erro 403 - Forbidden
- Verifique credenciais AWS
- Confirme se a conta de associado está ativa
- Verifique se a PAAPI 5.0 está habilitada

### Erro 500 - Internal Server Error
- Verifique logs do Vercel
- Confirme variáveis de ambiente
- Teste conexão com Supabase

### Produto não encontrado
- Verifique se o ASIN é válido
- Confirme disponibilidade na região configurada

