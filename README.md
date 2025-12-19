# MCP SonarQube Server

Servidor Model Context Protocol (MCP) para integração com SonarQube, permitindo acesso às funcionalidades de análise de código via MCP.

## 🚀 Quick Start

### Método 1: Usando uvx (Recomendado) ⭐

**Pré-requisito**: Instale o `uv` primeiro:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Configuração no Cursor:**

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "uvx",
      "args": [
        "git+https://github.com/JoaobatistaJuniorTR/mcp-sonar.git",
        "mcp-sonarqube"
      ],
      "env": {
        "SONARQUBE_URL": "https://sonar.qa.thomsonreuters.com",
        "SONARQUBE_TOKEN": "seu_token_aqui"
      }
    }
  }
}
```

**⚠️ IMPORTANTE**: Substitua `seu_token_aqui` pelo seu token do SonarQube.

### Método 2: Execução Direta do GitHub (Fallback)

Se `uvx` não estiver disponível, use:

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "python",
      "args": [
        "-c",
        "import urllib.request, sys, tempfile, subprocess, os; url='https://raw.githubusercontent.com/JoaobatistaJuniorTR/mcp-sonar/main/sonarqube_mcp_server.py'; f=tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8'); f.write(urllib.request.urlopen(url, timeout=30).read().decode('utf-8')); f.close(); subprocess.run([sys.executable, f.name], env=os.environ); os.unlink(f.name)"
      ],
      "env": {
        "SONARQUBE_URL": "https://sonar.qa.thomsonreuters.com",
        "SONARQUBE_TOKEN": "seu_token_aqui"
      }
    }
  }
}
```

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Acesso a um servidor SonarQube
- Token de autenticação do SonarQube
- `uv` instalado (para método uvx) ou Python com `mcp` e `requests`

## 🔧 Instalação

### Instalar uv (para usar uvx)

**Windows:**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalar dependências manualmente (se não usar uvx)

```bash
pip install mcp requests
```

### Como obter o token do SonarQube

1. Acesse o SonarQube
2. Vá em **My Account** > **Security**
3. Gere um novo token
4. Copie o token (ele só será exibido uma vez)

## 🛠️ Ferramentas Disponíveis

### 1. `search_issues`
Busca issues do SonarQube em projetos.

**Parâmetros:**
- `projectKeys` (array, opcional): Lista de chaves de projetos
- `severities` (array, opcional): Filtrar por severidade (BLOCKER, CRITICAL, MAJOR, MINOR, INFO)
- `statuses` (array, opcional): Filtrar por status (OPEN, CONFIRMED, REOPENED, RESOLVED, CLOSED)
- `pageSize` (integer, opcional): Tamanho da página (padrão: 100)
- `page` (integer, opcional): Número da página (padrão: 1)

**Exemplo:**
```
search_issues com projectKeys=["com.thomsonreuters:rt-data-scanner"] e severities=["CRITICAL", "MAJOR"]
```

### 2. `get_project_measures`
Obtém métricas de um projeto (cobertura, complexidade, linhas de código, etc.).

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto
- `metricKeys` (array, opcional): Lista de métricas a buscar

**Exemplo:**
```
get_project_measures com projectKey="com.thomsonreuters:rt-data-scanner" e metricKeys=["coverage", "ncloc", "complexity"]
```

### 3. `get_quality_gate_status`
Obtém o status do Quality Gate de um projeto.

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto

**Exemplo:**
```
get_quality_gate_status com projectKey="com.thomsonreuters:rt-data-scanner"
```

### 4. `list_projects`
Lista todos os projetos disponíveis no SonarQube.

**Parâmetros:**
- `page` (integer, opcional): Número da página

**Exemplo:**
```
list_projects
```

### 5. `get_project_issues_summary`
Obtém um resumo das issues de um projeto agrupadas por severidade e status.

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto

**Exemplo:**
```
get_project_issues_summary com projectKey="com.thomsonreuters:rt-data-scanner"
```

### 6. `ping_sonarqube`
Verifica se o servidor SonarQube está acessível.

**Exemplo:**
```
ping_sonarqube
```

## 📖 Exemplos de Uso

### Buscar todas as issues críticas de um projeto
```
search_issues com projectKeys=["com.thomsonreuters:rt-data-scanner"] e severities=["CRITICAL"]
```

### Obter métricas de cobertura
```
get_project_measures com projectKey="com.thomsonreuters:rt-data-scanner" e metricKeys=["coverage"]
```

### Verificar status do Quality Gate
```
get_quality_gate_status com projectKey="com.thomsonreuters:rt-data-scanner"
```

## 🔄 Métodos de Execução

### Método 1: uvx (Recomendado) ⭐

O `uvx` é similar ao `npx` do Node.js - executa pacotes Python diretamente sem instalação prévia.

**Vantagens:**
- ✅ Sem necessidade de clonar o repositório
- ✅ Sem necessidade de instalar dependências manualmente
- ✅ Sempre usa a versão mais recente
- ✅ Isolamento de dependências

### Método 2: Clonar e Executar Localmente

```bash
git clone https://github.com/JoaobatistaJuniorTR/mcp-sonar.git
cd mcp-sonar
pip install -r requirements.txt
```

Depois configure no Cursor:

```json
{
  "mcpServers": {
    "sonarqube": {
      "command": "python",
      "args": [
        "C:\\caminho\\para\\mcp-sonar\\sonarqube_mcp_server.py"
      ],
      "env": {
        "SONARQUBE_URL": "https://sonar.qa.thomsonreuters.com",
        "SONARQUBE_TOKEN": "seu_token_aqui"
      }
    }
  }
}
```

## 🆘 Troubleshooting

### Erro: "uvx: command not found"
Instale o `uv` primeiro (veja seção de instalação acima).

### Erro: "ModuleNotFoundError: No module named 'mcp'"
Se estiver usando o método manual, instale as dependências:
```bash
pip install mcp requests
```

### Erro: "SONARQUBE_URL e SONARQUBE_TOKEN devem ser configurados"
- Verifique se as variáveis estão no `env` do JSON
- Reinicie o Cursor após alterar a configuração

### Erro de autenticação
- Verifique se o token está correto e não expirou
- Certifique-se de que o token tem as permissões necessárias

### Erro de conexão
- Verifique se a URL do SonarQube está correta
- Verifique se há firewall ou proxy bloqueando a conexão

## 📝 Estrutura do Projeto

```
mcp-sonar/
├── sonarqube_mcp_server.py    # Servidor MCP principal
├── __main__.py                 # Entry point para execução modular
├── pyproject.toml              # Configuração do projeto (para uvx)
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
└── .gitignore                  # Arquivos ignorados pelo Git
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é para uso interno da organização.

## 🔗 Links

- [Repositório GitHub](https://github.com/JoaobatistaJuniorTR/mcp-sonar)
- [Documentação SonarQube API](https://docs.sonarqube.org/latest/extend/web-api/)
- [Documentação uv/uvx](https://github.com/astral-sh/uv)
