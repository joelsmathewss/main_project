CREATE DATABASE lucidcare;

-- extension for uuid
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users(
  user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_fullname VARCHAR(255) NOT NULL,
  user_email VARCHAR(255) NOT NULL,
  user_password VARCHAR(255) NOT NULL,
  user_age INTEGER,
  user_sex VARCHAR(50)
);
