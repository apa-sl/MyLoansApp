-- how to check constraints in a given table:
-- SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
-- FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
-- WHERE TABLE_NAME='TableName';

CREATE TABLE Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(50) NOT NULL,
  name VARCHAR(50) NOT NULL,
  password_hash NVARCHAR(128) NOT NULL
);

CREATE TABLE Vendors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE Loans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  user_id INT NOT NULL,
  vendor_id INT NOT NULL,
  status VARCHAR(25) NOT NULL DEFAULT "New",
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  agreement_id VARCHAR(50),
  due_day TINYINT NOT NULL,
  amount_total DECIMAL(7,2) NOT NULL,
  amount_outstanding DECIMAL(7,2) NOT NULL,
  status TINYINT NOT NULL,
  FOREIGN KEY (vendor_id) REFERENCES Vendors(id),
  FOREIGN KEY (user_id) REFERENCES Users(id)
  CHECK(due_day>0 AND due_day <=31)
);

CREATE TABLE Installments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  loan_id INT NOT NULL,
  amount DECIMAL(7,2) NOT NULL,
  payment_date DATE,
  payment_status BOOLEAN DEFAULT False,
  FOREIGN KEY (loan_id) REFERENCES Loans(id),
  CHECK(amount>0)
);

-- CREATE TRIGGER afterpayment_update_outstanding
-- AFTER UPDATE
-- ON installements 
