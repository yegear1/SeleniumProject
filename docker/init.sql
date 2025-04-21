CREATE TABLE IF NOT EXISTS gpu_info (
    id SERIAL PRIMARY KEY,
    marca TEXT NOT NULL,
    nome TEXT NOT NULL,
    UNIQUE (marca, nome)
);

CREATE TABLE IF NOT EXISTS website_id (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    UNIQUE (id, name)
);

CREATE TABLE IF NOT EXISTS gpu_prices (
    gpu_id INTEGER NOT NULL,
    website_id INTEGER NOT NULL,
    preco NUMERIC NOT NULL,
    data DATE NOT NULL,
    FOREIGN KEY (gpu_id) REFERENCES gpu_info(id),
    FOREIGN KEY (website_id) REFERENCES website_id(id),
    UNIQUE (gpu_id, website_id, data) 

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_gpu_prices_gpu_id ON gpu_prices(gpu_id);
CREATE INDEX IF NOT EXISTS idx_gpu_prices_data ON gpu_prices(data);
CREATE INDEX IF NOT EXISTS idx_gpu_prices_website_id ON gpu_prices(website_id);
