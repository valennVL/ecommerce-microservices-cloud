-- Seed data for products_db
-- Tables are created here so seed data can be inserted on first startup

CREATE TABLE IF NOT EXISTS products (
    id       INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(255),
    price    DOUBLE,
    quantity INT
);

INSERT IGNORE INTO products (name, price, quantity)
VALUES
  ('Laptop',    999.99, 10),
  ('Mouse',      19.99, 50),
  ('Keyboard',   49.99, 30),
  ('Monitor',   299.99, 15),
  ('USB Hub',    14.99, 40);
