-- Создание базы данных 
-- CREATE DATABASE Mozhevitina;

-- 1. Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    created_at DATE DEFAULT CURRENT_DATE
);

-- 2. Таблица товаров
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    image VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    production VARCHAR(100),
    description TEXT,
    composition TEXT,
    price NUMERIC(10, 2) CHECK (price > 0),
    stock INTEGER DEFAULT 0 CHECK (stock >= 0),
    discount_percent INTEGER DEFAULT 0
);

-- 3. Добавление тестовых пользователей
INSERT INTO users (login, role, last_name, first_name, middle_name) VALUES 
('admin', 'Администратор', 'Иванов', 'Иван', 'Сергеевич'),
('manager1', 'Менеджер', 'Петров', 'Пётр', 'Алексеевич'),
('client01', 'Клиент', 'Сидоров', 'Алексей', 'Иванович');

-- 4. Добавление тестовых товаров
INSERT INTO products (category, name, production, price, stock, discount_percent) VALUES 
('Кольца', 'Кольцо Линия', 'Грань', 2990.00, 48, 15),
('Кольца', 'Кольцо Волна', 'ЮвелирЛайн', 3390.00, 57, 15),
('Браслеты', 'Браслет Цепь', 'Грань', 3990.00, 48, 10),
('Цепочки', 'Цепочка Якорная', 'Грань', 4490.00, 48, 20);