# SeleniumProject

Este projeto é um scraper de preços de placas de vídeo dos sites Kabum, Pichau e Terabyte. Ele coleta os preços, armazena os dados em um banco de dados PostgreSQL e exibe os resultados em um dashboard interativo usando Dash.

## Funcionalidades

- **Scraping de Preços**: Coleta preços de placas de vídeo dos sites Kabum, Pichau e Terabyte usando Selenium.
- **Armazenamento de Dados**: Salva os dados coletados em um banco de dados PostgreSQL.
- **Dashboard Interativo**: Exibe os preços das placas de vídeo ao longo do tempo em um dashboard web, com opções para visualizar uma GPU específica ou todas as GPUs de uma vez.

## Estrutura do Projeto

- `main.py`: Script principal que executa o scraping e salva os dados no banco.
- `scrapers.py`: Contém as funções de scraping para cada site (Kabum, Pichau, Terabyte).
- `utils.py`: Funções utilitárias, como conexão com o banco (`connect_db`) e normalização de preços (`normalize_price`).
- `dashboard.py`: Cria o dashboard interativo com Dash para visualizar os preços.
- `logs/`: Diretório onde os logs do scraping são salvos.

## Estrutura do Banco de Dados

O projeto usa um banco de dados PostgreSQL com as seguintes tabelas:

- `gpu_info`: Armazena informações das GPUs (marca, nome).

  ```sql
  CREATE TABLE IF NOT EXISTS gpu_info (
      id SERIAL PRIMARY KEY,
      marca TEXT NOT NULL,
      nome TEXT NOT NULL,
      UNIQUE (marca, nome)
  );
  ```
- `website_id`: Armazena os sites (Kabum, Pichau, Terabyte).

  ```sql
  CREATE TABLE IF NOT EXISTS website_id (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      UNIQUE (id, name)
  );
  ```
- `gpu_prices`: Armazena os preços das GPUs por site e data.

  ```sql
  CREATE TABLE IF NOT EXISTS gpu_prices (
      gpu_id INTEGER NOT NULL,
      website_id INTEGER NOT NULL,
      preco NUMERIC NOT NULL,
      data DATE NOT NULL,
      FOREIGN KEY (gpu_id) REFERENCES gpu_info(id),
      FOREIGN KEY (website_id) REFERENCES website_id(id),
      UNIQUE (gpu_id, website_id, data)
  );
  CREATE INDEX IF NOT EXISTS idx_gpu_prices_gpu_id ON gpu_prices(gpu_id);
  CREATE INDEX IF NOT EXISTS idx_gpu_prices_data ON gpu_prices(data);
  CREATE INDEX IF NOT EXISTS idx_gpu_prices_website_id ON gpu_prices(website_id);
  ```

## Pré-requisitos

- Python 3.8+
- PostgreSQL
- Dependências Python (instale com `pip install -r requirements.txt`):
  - `selenium`
  - `psycopg2-binary`
  - `dash`
  - `pandas`
  - `sqlalchemy`
  - `apscheduler`

## Configuração

1. **Clone o Repositório**:

   ```bash
   git clone https://github.com/seu_usuario/gpu-price-scraper.git
   cd gpu-price-scraper
   ```

2. **Crie um Ambiente Virtual e Instale as Dependências**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure o Banco de Dados**:

   - Crie um banco de dados PostgreSQL chamado `gpus_db`.
   - Execute os comandos SQL acima para criar as tabelas.
   - Configure as variáveis de ambiente para a conexão com o banco:

     ```bash
     export POSTGRES_DB="gpus_db"
     export POSTGRES_USER="postgres"
     export POSTGRES_PASSWORD="postgres"
     export POSTGRES_HOST="localhost"
     export POSTGRES_PORT="5432"
     ```

     No Windows, use `set` em vez de `export`.

4. **Configure o Selenium**:

   - Instale o ChromeDriver compatível com sua versão do Chrome e adicione ao PATH.

## Uso

1. **Executar o Scraping**:

   - Rode o script principal para coletar os preços e salvar no banco:

     ```bash
     python main.py
     ```
   - Os logs do scraping serão salvos no diretório `logs/`.

## Licença

Este projeto está licenciado sob a MIT License.
