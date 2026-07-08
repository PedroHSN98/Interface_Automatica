# AutoHub Pro — Central de Automações

Central de automações internas com **duas interfaces**: um app desktop (Tkinter) e uma interface web (Flask), ambas rodando sobre os mesmos módulos de automação em Python.

---

## Especificações Técnicas

| Item | Detalhe |
|---|---|
| Linguagem | Python 3.13 |
| Interface desktop | Tkinter (nativo do Python) |
| Interface web | Flask + Server-Sent Events (log em tempo real no navegador) |
| Sistema operacional | Windows (10 / 11) |
| Fonte de UI (desktop) | Segoe UI / Consolas (nativas do Windows) |

---

## Funcionalidades

O app é organizado em módulos, cada um acessível tanto pela janela desktop quanto pela página web (`http://localhost:5000`):

### 📊 Dashboard
Visão geral do sistema: status das últimas execuções de cada módulo, atalhos rápidos.

### 📋 Analisador de Logs
Conecta via **SSH** (usuário/senha do `.env`) aos servidores Elasticsearch e Liferay configurados, executa `grep` remoto por um conjunto de padrões de erro conhecidos (exceptions, LDAP, broken pipe, templates FTL, etc.) e monta um relatório de ocorrências por data/servidor.

- **Entrada:** datas (dd/mm/aaaa) + seleção de quais servidores Elastic/Liferay consultar
- **Saída:** relatório no terminal da interface, com exportação para `.txt` e `.xlsx`

### 🗂️ Scraper de Imagens
Varre uma lista de URLs (`.txt`), baixa imagens dentro da faixa de **40 KB a 2 MB**, evita duplicadas (hash) e gera um relatório em Excel.

- **Entrada:** arquivo com uma URL por linha
- **Saída:** imagens salvas na pasta configurada + planilha `registro_noticias.xlsx`
- Paralelismo de 5 threads simultâneas

### 🕵️ AMAWeb — Avaliador de Acessibilidade
Acessa o portal `amaweb.unifesp.br` para cada URL da lista, extrai a nota de acessibilidade via Chrome **headless** (Selenium) e grava um histórico comparável entre execuções.

- **Entrada:** arquivo com uma URL/domínio por linha + nota mínima aceitável (threshold)
- **Saída:** planilha `.xlsx` com nota por site + `historico_amaweb.json`
- Timeout de 180 s por site

### 📄 Relatório Consolidado
Junta os dados de todos os módulos (logs, scraper, AMAWeb etc.) em uma única planilha Excel formatada, pronta para envio/arquivamento.

- **Saída:** `relatorio_consolidado.xlsx`

### 📜 Histórico
Tela com o histórico das últimas execuções de todos os módulos (status, data/hora e detalhes), gravado em `historico.json`.

---

## Documentação em PDF

Além deste README, o projeto inclui **dois manuais em PDF prontos**, gerados automaticamente e versionados no repositório — úteis para quem for instalar ou usar o AutoHub Pro sem precisar ler o código:

| Arquivo | Conteúdo |
|---|---|
| **`AutoHub_Pro_Manual_Instalacao.pdf`** | Passo a passo completo de **instalação** do zero (pré-requisitos, ambiente virtual, dependências, execução) |
| **`AutoHub_Pro_Documentacao.pdf`** | Documentação **funcional** do projeto: o que cada módulo faz, entradas e saídas |

Esses PDFs podem ser regenerados a qualquer momento (útil após alterar features), com:

```powershell
python gerar_pdf.py             # regenera o Manual de Instalação
python gerar_documentacao.py    # regenera a Documentação do Projeto
```

> Ambos os scripts usam a biblioteca `fpdf` (`pip install fpdf2`), não incluída no `requirements.txt` por não ser necessária para rodar o app — apenas para regerar os PDFs.

---

## Pré-requisitos

### 1. Python 3.13
Baixe em [python.org/downloads](https://www.python.org/downloads/). Durante a instalação marque **"Add Python to PATH"**.

Verifique após instalar:
```powershell
python --version
```

### 2. Google Chrome
Necessário apenas para o módulo **AMAWeb**. Instale em [google.com/chrome](https://www.google.com/chrome/).

### 3. ChromeDriver
Deve corresponder à versão do Chrome instalado. O projeto usa `selenium>=4.18`, que já resolve o driver automaticamente na maioria dos casos. Se não funcionar, baixe manualmente em [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads) e coloque o executável em uma pasta do PATH (ex: `C:\Windows\System32`).

### 4. Credenciais SSH (apenas para o Analisador de Logs)
O módulo de logs precisa de usuário/senha para conectar via SSH aos servidores Elasticsearch/Liferay. Essas credenciais **nunca** vão para o Git — ficam em um arquivo `.env` local (veja Passo 6 abaixo).

---

## Passo a Passo — Instalação

### Passo 1 — Clonar/copiar o projeto
```powershell
git clone https://github.com/PedroHSN98/Interface_Automatica.git
cd Interface_Automatica
```
Se for copiar a pasta manualmente entre computadores, **não copie `.venv`** — ela será recriada.

### Passo 2 — Criar o ambiente virtual
```powershell
python -m venv .venv
```

### Passo 3 — Ativar o ambiente virtual
```powershell
.venv\Scripts\activate
```

### Passo 4 — Instalar as dependências
```powershell
pip install -r requirements.txt
```

### Passo 5 — Configurar variáveis de ambiente
Copie o arquivo de exemplo e preencha com suas credenciais:
```powershell
copy .env.example .env
```
Edite `.env`:
```
LIFERAY_USUARIO=seu_usuario_aqui
LIFERAY_SENHA=sua_senha_aqui
```

### Passo 6 — Executar

**Interface Desktop (Tkinter):**
```powershell
python app.py
```

**Interface Web (Flask):**
```powershell
run_web.bat
```
ou manualmente:
```powershell
python web\server.py
```
Depois acesse **http://localhost:5000** no navegador (abre automaticamente).

---

## Criar Atalho na Área de Trabalho (opcional)

Com o ambiente virtual ativado, execute:
```powershell
python criar_atalho.py
```
Isso gera o ícone (`assets/icon.ico`) e cria `AutoHub Pro.lnk` na Área de Trabalho, apontando para `pythonw.exe` (sem janela de console).

---

## Configuração

As preferências de cada módulo (caminhos de arquivos, tema, intervalos, thresholds) ficam salvas em `config.json`, na raiz do projeto, e são editáveis diretamente pela interface (desktop ou web) — não é necessário editar esse arquivo manualmente. Ele é recriado com valores padrão caso não exista.

---

## Dependências Python

Todas listadas em `requirements.txt`:

| Pacote | Para que serve |
|---|---|
| `requests` | Requisições HTTP (scraper, amaweb) |
| `beautifulsoup4` | Parse de HTML (scraper) |
| `pandas` / `openpyxl` | Geração e leitura de planilhas Excel |
| `tqdm` | Barras de progresso em terminal |
| `selenium` | Automação do Chrome (AMAWeb) |
| `paramiko` | Conexão SSH aos servidores (Analisador de Logs) |
| `python-dotenv` | Carrega credenciais do `.env` |
| `pillow` | Geração do ícone `.ico` do atalho |
| `plyer` | Notificações nativas do Windows |
| `flask` | Interface web |
| `tkinter` | Interface desktop (já incluso no Python) |

Instale tudo de uma vez:
```powershell
pip install -r requirements.txt
```

---

## Estrutura do Projeto

```
interface_automacao/
├── app.py                    # ponto de entrada da interface desktop
├── criar_atalho.py           # gera atalho + ícone na Área de Trabalho
├── gerar_pdf.py               # gera AutoHub_Pro_Manual_Instalacao.pdf
├── gerar_documentacao.py      # gera AutoHub_Pro_Documentacao.pdf
├── run_web.bat                # inicia a interface web
├── requirements.txt
├── .env.example                # modelo de credenciais (copiar para .env)
├── config.json                 # preferências salvas pela interface
├── historico.json              # histórico de execuções
├── historico_amaweb.json       # histórico de notas do AMAWeb
├── automations/                # lógica de cada módulo
│   ├── logs.py
│   ├── scraper.py
│   ├── amaweb.py
│   └── relatorio.py
├── config/
│   ├── settings.py             # load/save do config.json
│   └── theme.py                # tema claro/escuro da UI desktop
├── ui/
│   └── app.py                  # janela Tkinter (todas as páginas/abas)
├── web/
│   ├── server.py                # rotas Flask
│   ├── templates/index.html
│   └── static/ (app.js, style.css)
├── utils/
│   ├── historico.py             # registra/lista execuções
│   └── notificacao.py           # notificações do Windows
├── assets/                      # ícone gerado (criar_atalho.py)
├── result-txt/                  # arquivos de entrada/saída de exemplo
└── galeria_noticias/             # saída padrão do Scraper
```

---

## Solução de Problemas

**`ModuleNotFoundError`** ao abrir o app
> O ambiente virtual não está ativo ou as dependências não foram instaladas. Repita os Passos 3 e 4.

**`ChromeDriver não iniciado`** (módulo AMAWeb)
> O Google Chrome não está instalado, ou o driver está desatualizado. Instale/atualize o Chrome e reinstale o selenium: `pip install --upgrade selenium`.

**Falha de conexão SSH** (módulo Analisador de Logs)
> Verifique se `.env` existe e contém `LIFERAY_USUARIO`/`LIFERAY_SENHA` válidos, e se a máquina tem acesso de rede aos servidores internos.

**Tkinter não encontrado**
> Reinstale o Python marcando a opção **"tcl/tk and IDLE"** durante a instalação.

**Interface web não abre**
> Confira se a porta 5000 está livre e se o Flask foi instalado (`pip install flask`). O `run_web.bat` instala automaticamente se faltar.
