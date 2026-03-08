# 📄 Automação de Geração de Contratos com Python

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Automation](https://img.shields.io/badge/Automation-Document%20Pipeline-green)
![Excel 365](https://img.shields.io/badge/Excel-365-217346?logo=microsoft-excel)
![API](https://img.shields.io/badge/API-Integration-orange)
![Status](https://img.shields.io/badge/Status-Production-success)

---

# 📌 Visão Geral

Este projeto feito no meu Estágio implementa uma **pipeline automatizada de geração e assinatura de contratos** utilizando **Python**, integrando dados de **Excel 365**, validação de **CNPJ via API pública** e envio automático para assinatura digital via **API da Autentique**.

A automação foi desenvolvida para substituir um processo manual de geração de contratos que envolvia:

- Copiar dados do Excel
- Preencher manualmente contratos
- Exportar documentos
- Enviar para assinatura digital

Com a automação, todo o processo passou a ser executado **de forma totalmente automatizada**, reduzindo drasticamente o tempo operacional e eliminando erros humanos.

---

# �️ Instalação e Configuração

## Pré-requisitos

- Python 3.12+
- Conta na [Autentique](https://autentique.com.br/) para obter token API
- Acesso à planilha Excel 365 hospedada no OneDrive/SharePoint

## Passos de Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/contrato-aut.git
   cd contrato-aut
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou venv\Scripts\activate no Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edite o `.env` com suas chaves reais:
     ```
     AUTENTIQUE_TOKEN=sua_chave_api_aqui
     EXCEL_URL=https://seu-link-sharepoint-aqui
     ```

5. **Execute a aplicação**:
   ```bash
   python app.py
   ```

## ⚠️ Segurança e Configuração

- **Nunca commite o arquivo `.env`** no repositório (já está no `.gitignore`).
- Cada usuário/vendedor deve configurar seu próprio `.env` com suas credenciais.
- Para distribuição, forneça apenas o `.env.example` como template.

---

# �🚀 Funcionalidades

## 📥 Integração com Excel 365

O sistema baixa automaticamente os dados da planilha hospedada no **Excel 365**, contendo informações dos expositores do evento.

Entre os dados coletados:

- Nome Fantasia
- CNPJ
- Nome do Sócio
- Email
- Tipo de Stand
- Forma de Pagamento

---

## 🧹 Tratamento e Validação de Dados

Antes da geração dos contratos, os dados passam por uma etapa de **limpeza e validação**:

- Remoção de caracteres especiais do CNPJ
- Validação estrutural de CNPJ
- Validação de email com regex
- Normalização de campos de texto
- Tratamento de campos vazios

Também são gerados **logs detalhados para debugging**, permitindo acompanhar cada etapa da execução.

---

## 📊 Validação de CNPJ via API

Antes de gerar o contrato, o sistema consulta automaticamente uma **API pública de CNPJ** para verificar:

- Situação cadastral da empresa
- Dados cadastrais básicos
- Quadro societário (quando disponível)

O contrato só é gerado se:

- O **CNPJ estiver ativo**
- Os dados forem considerados válidos

Isso evita geração de contratos para empresas inativas ou com dados incorretos.

---

## 📄 Geração Automática de Contratos

O sistema utiliza **templates DOCX dinâmicos** para gerar contratos personalizados.

Os templates são selecionados automaticamente com base em:

- **Tipo de stand** (STAND ou FOOD)
- **Forma de pagamento** (PIX, parcelado, etc.)

Os dados são organizados em dois dicionários principais:

### Dados do Evento
- Nome do evento
- Datas
- Informações institucionais

### Dados do Expositor
- Dados da empresa
- Dados do sócio responsável
- Condições comerciais

Esses dados são renderizados dinamicamente dentro dos templates.

---

## 📑 Conversão para PDF

Após gerar o contrato em DOCX, o sistema converte automaticamente o documento para **PDF**, preparando-o para envio à plataforma de assinatura digital.

---

## ✍️ Envio Automático para Assinatura Digital

Os contratos são enviados automaticamente para assinatura através da **API da Autentique**, incluindo:

- Upload do documento
- Definição de signatários
- Configuração de envio por email

Caso ocorram erros (como email inválido), o sistema registra o problema nos logs.

---

# ⚙️ Pipeline de Automação

A pipeline completa segue as seguintes etapas:

1️⃣ Download da planilha do **Excel 365**

2️⃣ Leitura dos dados com **Pandas**

3️⃣ Limpeza e tratamento dos dados

4️⃣ Validação de CNPJ via API

5️⃣ Seleção do template de contrato adequado

6️⃣ Geração do contrato DOCX

7️⃣ Conversão automática para PDF

8️⃣ Envio para assinatura via **Autentique API**

9️⃣ Registro de logs detalhados da execução

---

# 📊 Performance

Antes da automação, o processo de geração de contratos era totalmente manual.

### Processo Manual

⏱ **Tempo médio por contrato:** ~20 minutos

Etapas envolviam:

- Copiar dados da planilha
- Preencher contrato manualmente
- Exportar documento
- Enviar para assinatura

---

### Processo Automatizado

⚡ **Tempo médio por contrato:** ~20 segundos

Incluindo:

- leitura da planilha
- validação de CNPJ
- geração de contrato
- conversão para PDF
- envio para assinatura digital

---

# 📉 Redução de Tempo Operacional

A automação reduziu o tempo de processamento em aproximadamente:

## **98.3% de redução no tempo**

Comparação:

| Processo | Tempo |
|--------|--------|
Manual | 20 minutos |
Automação | 20 segundos |

Isso representa uma melhoria de aproximadamente **60x na velocidade do processo**.

---

# 📦 Distribuição e Implantação

## Para Desenvolvedores/Equipe Interna

Siga os passos de instalação acima. O repositório contém:

- Código fonte Python
- Templates de contrato
- Scripts de automação

## Para Usuários Finais (Vendedores)

### Opção 1: Executável (.exe) - Recomendado

1. Baixe o arquivo `app.exe` da seção **Releases** do GitHub.
2. Execute o `.exe` diretamente (não requer instalação do Python).
3. Configure o `.env` com suas credenciais (veja instruções abaixo).

### Opção 2: Código Fonte

1. Clone o repositório.
2. Instale Python 3.12+.
3. Siga os passos de instalação.
4. Execute `python app.py`.

## Configuração de Credenciais

Cada usuário deve configurar suas próprias credenciais:

1. Copie `.env.example` para `.env`.
2. Edite o `.env`:
   - `AUTENTIQUE_TOKEN`: Obtenha na [Autentique](https://autentique.com.br/).
   - `EXCEL_URL`: Link da planilha Excel 365 (OneDrive/SharePoint).

**Importante:** Nunca compartilhe seu `.env` com terceiros.

## Segurança

- Dados sensíveis (tokens, URLs) são armazenados localmente no `.env`.
- O `.env` não é incluído no repositório (protegido por `.gitignore`).
- Cada instalação requer configuração individual de credenciais.

---

# 🧠 Arquitetura da Automação

A aplicação foi estruturada de forma **modular**, separando responsabilidades entre funções e módulos.

### Componentes principais

**Leitura de Dados**
- Integração com Excel
- Parsing da planilha

**Validação**
- CNPJ
- Email
- Dados obrigatórios

**Geração de Contrato**
- Templates DOCX
- Renderização dinâmica

**Integração com APIs**
- API pública de CNPJ
- API da Autentique

**Logging**
- Registro detalhado da execução
- Identificação de erros e inconsistências

---

# 🔧 Tecnologias Utilizadas

- **Python 3.12**
- **Pandas**
- **Requests**
- **DocxTemplate**
- **Regex**
- **Excel 365**
- **Autentique API**

---

# 📈 Impacto do Projeto

Este projeto demonstra como **automação com Python pode transformar processos operacionais**, trazendo:

- Redução de **98% do tempo operacional**
- Eliminação de erros manuais
- Padronização na geração de contratos
- Integração direta com assinatura digital
- Escalabilidade para grandes volumes de documentos

---

# 🔒 Repositório

Este repositório é **privado**, pois contém integrações com APIs e dados sensíveis relacionados a contratos e empresas.

---

# 👤 Autor

**Kauã Dias**  
Estudante de Estatística | Data Science | Automação com Python

- 🐙 GitHub: https://github.com/Kauadp  
- 🔗 LinkedIn: https://www.linkedin.com/in/kauad/