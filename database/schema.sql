-- Referensi skema (setara dengan model SQLAlchemy di app/models.py).
-- Tabel dibuat otomatis oleh `python scripts/init_db.py`; file ini berguna untuk ERD (dbdiagram.io / DrawSQL).

CREATE TABLE IF NOT EXISTS users (
  id         BIGSERIAL PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,
  role       VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS categories (
  id   BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
  UNIQUE (name, type)
);

CREATE TABLE IF NOT EXISTS payment_methods (
  id   BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS transactions (
  id                BIGSERIAL PRIMARY KEY,
  user_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_id       BIGINT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
  payment_method_id BIGINT NOT NULL REFERENCES payment_methods(id) ON DELETE RESTRICT,
  type              VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
  amount            NUMERIC(15,2) NOT NULL CHECK (amount > 0),
  description       TEXT,
  transaction_date  DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions (user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions (category_id);

CREATE TABLE IF NOT EXISTS budgets (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
  amount      NUMERIC(15,2) NOT NULL CHECK (amount > 0),
  month       INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  year        INTEGER NOT NULL CHECK (year BETWEEN 2000 AND 2100),
  UNIQUE (user_id, category_id, month, year)
);
