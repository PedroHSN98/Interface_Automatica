# AutoHub Pro — Central de Automações

Interface desktop para automações internas, construída com Python + Tkinter.

---

## Especificações Técnicas

| Item | Detalhe |
|---|---|
| Linguagem | Python 3.13 |
| Interface gráfica | Tkinter (nativo do Python) |
| Sistema operacional | Windows (10 / 11) |
| Fonte de UI | Segoe UI (nativa do Windows) |
| Fonte do terminal | Consolas (nativa do Windows) |

---

## Funcionalidades

### 1. Analisador de Logs
Lê um arquivo XML no formato **log4j** e conta ocorrências de padrões de erro predefinidos, exibindo um relatório visual com barras de frequência.

- **Entrada:** arquivo `logs.xml`
- **Saída:** relatório no terminal da interface

### 2. Scraper de Imagens
Varre URLs listadas em um arquivo `.txt`, baixa imagens com tamanho entre **40 KB e 2 MB** e gera uma planilha Excel com o relatório de execução.

- **Entrada:** arquivo `links.txt` com uma URL por linha
- **Saída:** imagens salvas na pasta configurada + `registro_noticias.xlsx`
- Paralelismo de 5 threads simultâneas por URL

### 3. AMAWeb — Avaliador de Acessibilidade
Acessa cada URL listada no portal `amaweb.unifesp.br`, extrai a nota de acessibilidade exibida na página e grava os resultados em uma planilha Excel. Usa o Chrome no modo **headless**.

- **Entrada:** arquivo `urls.txt` com um domínio/URL por linha
- **Saída:** planilha `.xlsx` com URL e nota de cada site
- Timeout de 180 s por site

---

## Pré-requisitos

### 1. Python 3.13

Baixe em [python.org/downloads](https://www.python.org/downloads/).

Durante a instalação marque a opção **"Add Python to PATH"**.

Verifique após instalar:
```
python --version
```

### 2. Google Chrome

Instale a versão mais recente do Chrome em [google.com/chrome](https://www.google.com/chrome/).

### 3. ChromeDriver

O ChromeDriver deve estar na versão **correspondente ao Chrome instalado** e acessível no PATH do sistema.

**Como instalar via pip (recomendado):**
```
pip install webdriver-manager
```
> O projeto já usa `selenium>=4.18` com gerenciamento automático de driver.  
> Se o driver não for encontrado automaticamente, baixe manualmente em [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads) e coloque o executável em uma pasta que esteja no PATH (ex: `C:\Windows\System32`).

---

## Como Rodar em Outro Computador

### Passo 1 — Copiar o projeto

Copie toda a pasta `interface_automacao` para o novo computador. **Não copie a pasta `.venv`** — ela será recriada.

Estrutura esperada:
```
interface_automacao/
├── app.py
├── criar_atalho.py
├── requirements.txt
├── automations/
│   ├── amaweb.py
│   ├── logs.py
│   ├── scraper.py
│   └── __init__.py
├── config/
│   ├── theme.py
│   └── __init__.py
├── ui/
│   ├── app.py
│   ├── utils.py
│   └── __init__.py
└── assets/          (criado automaticamente)
```

### Passo 2 — Criar o ambiente virtual

Abra o terminal (PowerShell ou Prompt) dentro da pasta do projeto:

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

### Passo 5 — Executar o aplicativo

```powershell
python app.py
```

---

## Criar Atalho na Área de Trabalho (opcional)

Com o ambiente virtual ativado, execute:

```powershell
python criar_atalho.py
```

Isso irá:
- Gerar o ícone `assets/icon.ico`
- Criar um atalho `AutoHub Pro.lnk` na Área de Trabalho apontando para `pythonw.exe` (sem janela de console)

---

## Dependências Python

Todas listadas em `requirements.txt`:

| Pacote | Versão mínima | Para que serve |
|---|---|---|
| `requests` | 2.31.0 | Requisições HTTP (scraper e amaweb) |
| `beautifulsoup4` | 4.12.0 | Parse de HTML para extração de imagens |
| `pandas` | 2.0.0 | Geração e leitura de planilhas Excel |
| `openpyxl` | 3.1.0 | Leitura/escrita de arquivos `.xlsx` |
| `tqdm` | 4.66.0 | Barras de progresso em terminal |
| `selenium` | 4.18.0 | Automação do Chrome (AMAWeb) |
| `pillow` | 10.0.0 | Geração do ícone `.ico` do atalho |
| `tkinter` | — | Interface gráfica (já incluso no Python) |

Instale tudo de uma vez:
```powershell
pip install -r requirements.txt
```

---

## Estrutura de Arquivos de Entrada

### Analisador de Logs
```
logs_servidor/
└── logs.xml       ← arquivo XML no formato log4j
```

### Scraper de Imagens
```
fontes/
└── links.txt      ← uma URL por linha
```

### AMAWeb
```
urls.txt           ← um domínio ou URL por linha
```

---

## Arquivos de Saída

| Módulo | Arquivo gerado |
|---|---|
| Scraper | `galeria_noticias/registro_noticias.xlsx` + imagens `.jpg` |
| AMAWeb | `resultado.xlsx` (caminho configurável na interface) |

---

## Solução de Problemas

**`ModuleNotFoundError`** ao abrir o app
> O ambiente virtual não está ativo ou as dependências não foram instaladas. Execute os Passos 3 e 4 novamente.

**`ChromeDriver não iniciado`**
> O Google Chrome não está instalado, ou o ChromeDriver está desatualizado. Instale/atualize o Chrome e reinstale o selenium: `pip install --upgrade selenium`.

**Tkinter não encontrado**
> Reinstale o Python marcando a opção **"tcl/tk and IDLE"** durante a instalação.

**Fontes diferentes no Windows 10**
> A interface usa Segoe UI e Consolas — ambas nativas do Windows. Se estiver em outro SO, as fontes serão substituídas pelo sistema automaticamente.