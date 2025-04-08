-- Tabela 1: Informações das Placas
CREATE TABLE IF NOT EXISTS gpu_info (
    id SERIAL PRIMARY KEY,
    site TEXT NOT NULL,
    marca TEXT NOT NULL,
    nome TEXT NOT NULL,
    UNIQUE (marca, nome)
);

-- Tabela 2: Preços e Datas
CREATE TABLE IF NOT EXISTS gpu_prices (
    gpu_id INTEGER NOT NULL,
    preco NUMERIC,
    data DATE,
    FOREIGN KEY (gpu_id) REFERENCES gpu_info(id),
    UNIQUE (gpu_id, data) -- Evita duplicatas de preço na mesma data
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_gpu_prices_gpu_id ON gpu_prices(gpu_id);
CREATE INDEX IF NOT EXISTS idx_gpu_prices_data ON gpu_prices(data);
