# Guia de Implantação - Consultor de Notebooks

## Configuração de Variáveis de Ambiente no Vercel

Para que a API funcione corretamente, você precisa configurar as seguintes variáveis de ambiente no painel do Vercel:

### 1. Variáveis do Supabase
- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_SERVICE_KEY`: Chave de serviço do Supabase (com permissões de escrita)

### 2. Variáveis da Amazon PAAPI 5.0
- `AWS_ACCESS_KEY_ID`: Sua chave de acesso AWS
- `AWS_SECRET_ACCESS_KEY`: Sua chave secreta AWS
- `AWS_ASSOCIATE_TAG`: Sua tag de associado da Amazon
- `AWS_REGION`: Região AWS (padrão: us-east-1)

## Como Configurar no Vercel

1. Acesse o painel do Vercel (vercel.com)
2. Vá para o seu projeto
3. Clique em "Settings" > "Environment Variables"
4. Adicione cada variável listada acima

## Estrutura da Tabela no Supabase

Certifique-se de que sua tabela `notebooks` no Supabase tenha as seguintes colunas:

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

## Testando a API

Após a implantação, você pode testar a API fazendo uma requisição POST para:
`https://seu-projeto.vercel.app/api/update_notebooks`

Com o corpo da requisição:
```json
{
    "asin": "B08N5WRWNW"
}
```

## Requisitos da Amazon PAAPI 5.0

1. **Conta de Associado**: Você precisa ter uma conta ativa no programa de associados da Amazon
2. **Credenciais AWS**: Acesso às credenciais da PAAPI 5.0
3. **Aprovação**: Sua aplicação precisa estar aprovada para usar a PAAPI 5.0

## Troubleshooting

### Erro 403 - Forbidden
- Verifique se suas credenciais AWS estão corretas
- Confirme se sua conta de associado está ativa
- Verifique se a PAAPI 5.0 está habilitada para sua conta

### Erro 500 - Internal Server Error
- Verifique os logs do Vercel
- Confirme se todas as variáveis de ambiente estão configuradas
- Teste a conexão com o Supabase

### Produto não encontrado
- Verifique se o ASIN está correto
- Confirme se o produto está disponível na região configurada

