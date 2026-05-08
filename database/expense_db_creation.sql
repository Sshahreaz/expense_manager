CREATE DATABASE IF NOT EXISTS expense_manager;
USE expense_manager;

CREATE TABLE IF NOT EXISTS expenses (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    expense_date    DATE            NOT NULL,
    category        VARCHAR(255)    NOT NULL,
    amount          DECIMAL(10, 2)  NOT NULL,
    UNIQUE KEY date_category (expense_date, category)
);