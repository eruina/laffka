BEGIN TRANSACTION;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS btc;
CREATE TABLE "orders" (
	`index`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`address`	TEXT,
	`wif`	TEXT,
	`private_key`	TEXT,
	`paid`	INTEGER,
	`address_salt`	INTEGER,
	`item_index`	INTEGER,
	`item_amount`	INTEGER,
	`btc_address`	TEXT,
	`order_price`	REAL,
	`date`	INTEGER,
	`note`	TEXT
);
CREATE TABLE "items" (
	`name`	TEXT NOT NULL,
	`ind`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`price`	REAL NOT NULL,
	`visible`	INTEGER,
	`description`	TEXT,
	`pcs`	TEXT
);
INSERT INTO `items` VALUES ('Project hat',1,100.0,-1,'-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

Donations are pretty much welcome.
1KsxhDfYbF7Lg47wqeTgcZQgTVS18mzZrd
Laffka
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2

iF4EAREIAAYFAltvCL0ACgkQ2+cre6vr1tXROgD8DA+koJytuInHBb7EQVmOj37v
V5Y83aQrTm7F+UaLqrkBAJt5A48GnAWDYRfPm8dTIZpgEnPN0cOCf/mPRjQusqBe
=7yQ9
-----END PGP SIGNATURE-----','1,5,10,50,100');
CREATE TABLE `btc` (
	`rate`	REAL
);
INSERT INTO `btc` VALUES (40535.13);
COMMIT;
