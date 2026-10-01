-- Seed data for users_db
-- Tables are created here so seed data can be inserted on first startup

CREATE TABLE IF NOT EXISTS users (
    id       INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(255),
    email    VARCHAR(255) UNIQUE,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

INSERT IGNORE INTO users (name, email, username, password)
VALUES
  ('Juan',  'juan@gmail.com',  'juan',  '123'),
  ('Maria', 'maria@gmail.com', 'maria', '456'),
  ('Admin', 'admin@gmail.com', 'admin', 'admin');
