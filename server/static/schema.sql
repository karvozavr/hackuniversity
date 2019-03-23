DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS reservation_eq;

CREATE TABLE orders
(
  id         TEXT PRIMARY KEY,
  product_id TEXT NOT NULL,
  amount     INT  NOT NULL CHECK (amount >= 0),
  deadline   TIMESTAMP
);

CREATE TABLE products
(
  id              TEXT PRIMARY KEY,
  equipment_class TEXT[] NOT NULL
);

CREATE TABLE equipment
(
  id              TEXT PRIMARY KEY,
  equipment_class TEXT NOT NULL,
  speed_per_hour  INT  NOT NULL CHECK (speed_per_hour >= 0),
  available_hours INT  NOT NULL
);

CREATE TABLE reservation_eq
(
  id           TEXT PRIMARY KEY,
  equipment_id TEXT      NOT NULL,
  order_id     TEXT      NOT NULL,
  amount       INT       NOT NULL CHECK ( amount >= 0 ),
  start_time   TIMESTAMP NOT NULL,
  finish_time  TIMESTAMP NOT NULL
);