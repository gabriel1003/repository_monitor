# Repository Monitor (Monitorador de Repositórios GitHub)

Este projeto é uma aplicação Python projetada para monitorar e organizar repositórios GitHub de uma organização específica. Ele coleta informações sobre os repositórios (públicos e privados), associa-os a projetos internos definidos pelo usuário e armazena esses dados em um banco de dados SQLite para futuras análises.

## 🎯 Objetivo

O principal objetivo deste projeto é fornecer uma solução automatizada para:

* Consumir a API do GitHub para listar todos os repositórios de uma organização.
* Classificar cada repositório como público ou privado.
* Extrair informações relevantes (nome, visibilidade, datas de criação/atualização, estrelas, forks, URL).
* Armazenar esses dados em um banco de dados relacional SQLite.
* Estabelecer um relacionamento entre repositórios e projetos internos da empresa (um repositório pertence a um projeto, um projeto pode ter vários repositórios).
* Atribuir repositórios a projetos internos com base em regras configuráveis via arquivo YAML.
* Implementar tratamento de erros robusto e evitar duplicações.

## 📦 Requisitos Técnicos

* Python 3.8+
* Banco de dados SQLite (já integrado ao Python)

## 📁 Estrutura do Projeto
```plaintext
repository_monitor/
├── main.py               # Ponto de entrada principal da aplicação
├── requirements.txt      # Dependências do projeto
├── app.log               # Arquivo de log da aplicação

├── data/
│   ├── projetos.csv      # Dados dos projetos internos e nome da organização
│   ├── projetos.json     # (Alternativa ao CSV)
│   └── project_assignment_rules.yaml # Regras para associar repositórios a projetos
├── repos_monitor.db      # Banco de dados SQLite gerado
└── src/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── config.py     # Configurações gerais da aplicação e logging
    ├── models/
    │   ├── __init__.py
    │   └── model.py     # Camada de modelo de dados (interação com SQLite)
    └── services/
        ├── __init__.py
        ├── github_api.py # Interação com a API do GitHub
        ├── project_importer.py # Importação de projetos de CSV/JSON
        └── rule_loader.py    # Carregamento das regras de atribuição (YAML)
```
  
  ## 🚀 Como Rodar a Aplicação
      Siga os passos abaixo para configurar e executar o projeto:


  ### 1. Clonar o Repositório (Exemplo)

```bash
  git clone [https://github.com/gabriel1003/repository_monitor.git](https://github.com/gabriel1003/repository_monitor.git)
  cd repository_monitor      
```


### 2. Configurar Ambiente Virtual (Altamente Recomendado)

Crie e ative um ambiente virtual para isolar as dependências do projeto:

```bash
python -m venv venv
```

* No Windows:

```bash
.\venv\Scripts\activate
```

* No macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Instalar Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias listadas em requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configurar o GitHub Personal Access Token (PAT)

Para acessar a API do GitHub, você precisa de um Personal Access Token (PAT):

1. Vá para as Configurações do GitHub > Developer settings > Personal access tokens > Tokens (classic).

2. Clique em "Generate new token (classic)".

3. Dê um nome para o token (ex: repo-monitor-app).

4. Defina um prazo de validade (ou "No expiration" com cautela).

5. Conceda a permissão (scope) repo (para acessar repositórios públicos e privados da organização).

6. Copie o token gerado IMEDIATAMENTE! Você não conseguirá vê-lo novamente.

7. Na raiz do seu projeto (test_from_gevu/), crie um arquivo chamado .env e adicione a seguinte linha, substituindo SEU_TOKEN_AQUI pelo seu token real:
GITHUB_TOKEN=ghp_SEU_TOKEN_AQUI
Importante: Adicione .env ao seu arquivo .gitignore para garantir que seu token nunca seja enviado para o controle de versão.

### 5. Preparar Arquivos de Dados

Crie a pasta data/ dentro do diretório repository_monitor/ se ela ainda não existir.

* data/projetos.csv (ou data/projetos.json): Este arquivo define os projetos internos da sua empresa e especifica a organização GitHub a ser monitorada.

```
organizacao_github,nome,descricao
SavanDevs,Projeto Jogo Alpha,Repositórios relacionados ao desenvolvimento do jogo Alpha,Documentacao do Jogo,Repositórios para documentação e wikis do jogo,Ferramentas de Desenvolvimento,Repositórios para ferramentas e utilitários internos do jogo
```

(Nota: A organizacao_github só precisa estar na primeira linha do CSV. Para JSON, no primeiro objeto da lista.)

* data/project_assignment_rules.yaml: Este arquivo contém as regras para a aplicação associar os repositórios aos projetos internos com base em palavras-chave no nome do repositório. Os project_name devem corresponder exatamente aos nomes definidos no projetos.csv.

```

rules:

* project_name: "Projeto Jogo Alpha"
    keywords:
  * "game"
  * "jogo"
  * "unity"
  * "unreal"
  * "dev"
* project_name: "Documentacao do Jogo"
    keywords:
  * "docs"
  * "documentation"
  * "wiki"
  * "manual"
* project_name: "Ferramentas de Desenvolvimento"
    keywords:
  * "tools"
  * "util"
  * "scripts"
  * "automatizacao"
  * "build"
  ```
### 6. Executar a Aplicação

Com todas as configurações no lugar e o ambiente virtual ativado, execute o script principal:

```bash
python main.py
```

### 7. Verificar a Saída e os Dados

* Observe a saída no terminal. Você verá mensagens de log detalhando o processo de configuração, importação de projetos, carregamento de regras, coleta de repositórios e armazenamento no banco de dados.
* Um arquivo de log chamado app.log será criado na raiz do projeto com um registro detalhado.
* Um arquivo de banco de dados SQLite chamado repos_monitor.db será criado na pasta data.

## 📊 Visualizando os Dados do Banco de Dados

Para explorar o conteúdo do repos_monitor.db, recomendamos usar uma ferramenta de interface gráfica:

* DB Browser for SQLite: Uma ferramenta gratuita e fácil de usar. Baixe em [https://sqlitebrowser.org/].
* Extensão SQLite para VS Code: Se você usa o Visual Studio Code, instale a extensão "SQLite" (Publicadora: alexcvzz). Após a instalação, clique no ícone de banco de dados na barra lateral esquerda, clique em "Open Database" e selecione seu arquivo repos_monitor.db. Você poderá então navegar pelas tabelas Projetos e Repositorios e ver os dados.

## 🔒 Considerações de Segurança

* Gerenciamento de Segredos: O Personal Access Token do GitHub é armazenado em um arquivo .env e carregado via variáveis de ambiente, garantindo que ele não seja hardcoded nem versionado.
* Permissões Mínimas: O PAT deve ter apenas as permissões (scopes) necessárias (repo é suficiente para este projeto).
* Tratamento de Rate Limiting: A aplicação respeita os limites de requisição da API do GitHub para evitar bloqueios.
* Logging: O sistema de logging ajuda a monitorar a execução e identificar potenciais anomalias ou erros de segurança.
