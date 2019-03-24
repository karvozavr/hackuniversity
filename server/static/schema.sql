DROP TABLE IF EXISTS "order" CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS reservation_eq CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS eq_hist_data CASCADE;

CREATE TABLE product
(
  id              TEXT PRIMARY KEY,
  equipment_class TEXT[] NOT NULL
);

CREATE TABLE "order"
(
  id         TEXT PRIMARY KEY,
  product_id TEXT NOT NULL REFERENCES product (id),
  amount     INT  NOT NULL CHECK (amount >= 0),
  deadline   TIMESTAMP
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
  id           SERIAL PRIMARY KEY,
  equipment_id TEXT      NOT NULL,
  order_id     TEXT      NOT NULL,
  amount       INT       NOT NULL CHECK ( amount >= 0 ),
  start_time   TIMESTAMP NOT NULL,
  finish_time  TIMESTAMP NOT NULL
);

CREATE TABLE "user"
(
  id         TEXT PRIMARY KEY,
  password   TEXT NOT NULL,
  privileges INT  NOT NULL CHECK ( privileges = 0 OR privileges = 1 )
);

CREATE TABLE eq_hist_data
(
  id              TEXT      NOT NULL,
  "day"           TIMESTAMP NOT NULL,
  idle            DECIMAL   NOT NULL,
  "work"          DECIMAL   NOT NULL,
  repair          DECIMAL   NOT NULL,
  equipment_class TEXT      NOT NULL,
  PRIMARY KEY (id, "day")
);