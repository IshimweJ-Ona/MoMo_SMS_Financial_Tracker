-- database/database_setup.sql
-- MoMo SMS Financial Tracker Database Schema
-- Based on provided ERD design
-- Created: 2025-09-19

CREATE DATABASE IF NOT EXISTS momo_tracker;
USE momo_tracker;

-- Users table: Stores user information for MoMo transactions
CREATE TABLE IF NOT EXISTS Users (
  user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique user identifier',
  name VARCHAR(100) NOT NULL COMMENT 'Full name of the user',
  phone VARCHAR(20) NOT NULL UNIQUE COMMENT 'Phone number used in MoMo (unique)',
  email VARCHAR(100) COMMENT 'Optional user email address',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'User creation timestamp',
  CONSTRAINT chk_phone_format CHECK (phone REGEXP '^[0-9]{10,15}$')
) ENGINE=InnoDB COMMENT='User accounts for MoMo transactions';

-- Transaction Categories table: Defines types of financial transactions
CREATE TABLE IF NOT EXISTS Transaction_Categories (
  cat_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique category identifier',
  cat_name VARCHAR(50) NOT NULL COMMENT 'Name of transaction category',
  description VARCHAR(255) COMMENT 'Detailed description of the category',
  is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether category is currently active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Category creation timestamp'
) ENGINE=InnoDB COMMENT='Transaction type classifications';

-- Transactions table: Core financial transaction records
CREATE TABLE IF NOT EXISTS Transactions (
  txn_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique transaction identifier',
  sender_id INT NOT NULL COMMENT 'User ID of transaction sender',
  receiver_id INT NOT NULL COMMENT 'User ID of transaction receiver',
  amount DECIMAL(12,2) NOT NULL COMMENT 'Transaction amount (precision for financial data)',
  txn_date DATETIME NOT NULL COMMENT 'Transaction timestamp',
  category_id INT COMMENT 'Transaction category reference',
  status VARCHAR(30) DEFAULT 'pending' COMMENT 'Transaction status',
  raw_message TEXT COMMENT 'Original SMS message content',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
  FOREIGN KEY (sender_id) REFERENCES Users(user_id) ON DELETE RESTRICT,
  FOREIGN KEY (receiver_id) REFERENCES Users(user_id) ON DELETE RESTRICT,
  FOREIGN KEY (category_id) REFERENCES Transaction_Categories(cat_id) ON DELETE SET NULL,
  CONSTRAINT chk_amount_positive CHECK (amount > 0),
  CONSTRAINT chk_status_valid CHECK (status IN ('pending', 'completed', 'failed', 'cancelled', 'reconciled'))
) ENGINE=InnoDB COMMENT='Financial transaction records';

-- System Logs table: Audit trail for all transaction operations
CREATE TABLE IF NOT EXISTS System_Logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique log identifier',
  txn_id INT NOT NULL COMMENT 'Reference to transaction being logged',
  action VARCHAR(100) NOT NULL COMMENT 'Action performed (INSERT, UPDATE, DELETE)',
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Log entry timestamp',
  notes TEXT COMMENT 'Additional log information',
  user_id INT COMMENT 'User who performed the action',
  FOREIGN KEY (txn_id) REFERENCES Transactions(txn_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
  CONSTRAINT chk_action_valid CHECK (action IN ('INSERT', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT'))
) ENGINE=InnoDB COMMENT='Audit trail for transaction operations';

-- Performance Indexes
CREATE INDEX idx_users_phone ON Users(phone) COMMENT 'Index for phone number lookups';
CREATE INDEX idx_transactions_date ON Transactions(txn_date) COMMENT 'Index for date-based queries';
CREATE INDEX idx_transactions_status ON Transactions(status) COMMENT 'Index for status filtering';
CREATE INDEX idx_transactions_sender ON Transactions(sender_id) COMMENT 'Index for sender queries';
CREATE INDEX idx_transactions_receiver ON Transactions(receiver_id) COMMENT 'Index for receiver queries';
CREATE INDEX idx_transactions_category ON Transactions(category_id) COMMENT 'Index for category filtering';
CREATE INDEX idx_logs_transaction ON System_Logs(txn_id) COMMENT 'Index for transaction log lookups';
CREATE INDEX idx_logs_timestamp ON System_Logs(timestamp) COMMENT 'Index for time-based log queries';

-- Sample data (6+ records per main table)
INSERT INTO Users (name, phone, email) VALUES
('Alice Johnson', '0788000001', 'alice@example.com'),
('Bob Smith', '0788000002', 'bob@example.com'),
('Clara Davis', '0788000003', 'clara@example.com'),
('Daniel Wilson', '0788000004', 'daniel@example.com'),
('Eve Brown', '0788000005', 'eve@example.com'),
('Frank Miller', '0788000006', 'frank@example.com');

INSERT INTO Transaction_Categories (cat_name, description) VALUES
('Send Money', 'Peer to peer money transfer'),
('Withdraw', 'Cash withdrawal from account'),
('Deposit', 'Incoming money deposit'),
('Airtime', 'Mobile airtime purchase'),
('Merchant', 'Merchant payment'),
('Bill Payment', 'Utility and service bill payments');

INSERT INTO Transactions (sender_id, receiver_id, amount, txn_date, category_id, status, raw_message) VALUES
(1, 2, 15000.00, '2025-09-19 10:30:00', 1, 'completed', 'Sample: Send from 0788000001 to 0788000002'),
(2, 3, 5000.00, '2025-09-19 11:15:00', 4, 'completed', 'Sample: Airtime purchase by 0788000002'),
(3, 1, 20000.00, '2025-09-19 12:00:00', 3, 'completed', 'Sample: Deposit credited to 0788000003'),
(4, 5, 7500.00, '2025-09-19 13:45:00', 5, 'completed', 'Sample: Merchant payment to vendor'),
(5, 1, 12000.00, '2025-09-19 14:20:00', 2, 'completed', 'Sample: Withdraw by 0788000005'),
(6, 2, 8500.00, '2025-09-19 15:10:00', 1, 'pending', 'Sample: Pending transfer from 0788000006');

INSERT INTO System_Logs (txn_id, action, notes, user_id) VALUES
(1, 'INSERT', 'Imported from XML', 1),
(2, 'INSERT', 'Imported from XML', 2),
(3, 'INSERT', 'Imported from XML', 3),
(4, 'INSERT', 'Imported from XML', 4),
(5, 'INSERT', 'Imported from XML', 5),
(6, 'INSERT', 'Manual entry', 6);
