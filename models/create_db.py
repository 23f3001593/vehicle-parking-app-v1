import sqlite3

conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS User(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL CHECK(length(pincode)=6),
    role TEXT NOT NULL CHECK(role IN ('user','admin'))
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ParkingLot(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prime_location_name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL CHECK(length(pincode)=6),
    price NUMERIC NOT NULL,
    max_spots INTEGER NOT NULL,
    filled_spots INTEGER NOT NULL DEFAULT 0,
    revenue_collected NUMERIC NOT NULL DEFAULT 0.0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ParkingSpot(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'A' CHECK(status IN ('A','O')),
    FOREIGN KEY(lot_id) REFERENCES ParkingLot(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Reservation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    vehicle_num TEXT NOT NULL CHECK(length(vehicle_num)=10),
    parking_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    leaving_time DATETIME DEFAULT NULL,
    parking_cost NUMERIC DEFAULT NULL,
    FOREIGN KEY(spot_id) REFERENCES ParkingSpot(id),
    FOREIGN KEY(user_id) REFERENCES User(id)
)
''')

admin_data = ("ramkumar", "RamKumar9", "Ram Kumar", "12 MG Road, Bengaluru", "560001", "admin")
cursor.execute(
    "INSERT INTO User (user_name,password,full_name,address,pincode,role) VALUES (?,?,?,?,?,?)", admin_data
)

conn.commit()
cursor.close()
conn.close()