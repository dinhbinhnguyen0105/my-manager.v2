from src.my_constants import DB_TABLES

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {DB_TABLES["profile"]} (
    id VARCHAR PRIMARY KEY,
    mobile_ua: TEXT,
    desktop_ua: TEXT,
    uid: TEXT,
    status: TEXT,
    username: TEXT,
    password: TEXT,
    two_fa: TEXT,
    email: TEXT,
    email_password: TEXT,
    phone_number: TEXT,
    profile_note: TEXT,
    profile_type: TEXT,
    profile_group: INTEGER,
    profile_name: TEXT,
    created_at: TEXT,
    updated_at: TEXT
);
CREATE TABLE IF NOT EXISTS {DB_TABLES["property_product"]} (
    id VARCHAR PRIMARY KEY,
    pid: TEXT,
    status: TEXT,
    transaction_type: TEXT,
    province: TEXT,
    district: TEXT,
    ward: TEXT,
    street: TEXT,
    category: TEXT,
    area: REAL,
    price: REAL,
    unit: TEXT,
    legal: TEXT,
    structure: REAL,
    function: TEXT,
    building_line: TEXT,
    furniture: TEXT,
    description: TEXT,
    created_at: TEXT,
    updated_at: TEXT
);
CREATE TABLE IF NOT EXISTS {DB_TABLES["misc_product"]} (
    id VARCHAR PRIMARY KEY,
    status: TEXT,
    name: TEXT,
    description: TEXT,
    created_at: TEXT,
    updated_at: TEXT
);
CREATE TABLE IF NOT EXISTS {DB_TABLES["property_template"]} (
    id VARCHAR PRIMARY KEY,
    transaction_type: TEXT,
    name: TEXT,
    category: TEXT,
    value: TEXT,
    is_default: BOOLEAN,
    created_at: TEXT,
    updated_at: TEXT
);
CREATE TABLE IF NOT EXISTS {DB_TABLES["setting"]} (
    id VARCHAR PRIMARY KEY,
    name: TEXT,
    value: TEXT,
    is_selected: BOOLEAN,
    created_at: TEXT,
    updated_at: TEXT
);
"""
