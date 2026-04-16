from datetime import datetime
import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_tables()


    def create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            lang_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            name TEXT
        )
        """)
        self.cur.execute("PRAGMA table_info(user)")
        cols = [c[1] for c in self.cur.fetchall()]

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_uz TEXT,
            name_ru TEXT,
            name_en TEXT,
            parent_id INTEGER
        )
        """)
        self.cur.execute("""
        INSERT INTO category (name_uz, name_ru, name_en, parent_id)
        VALUES ('Lavash', 'Лаваш', 'Lavash', NULL)
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name_uz TEXT,
            name_ru TEXT,
            name_en TEXT,
            price REAL,
            description_uz TEXT,
            description_ru TEXT,
            description_en TEXT,
            photo TEXT,
            FOREIGN KEY(category_id) REFERENCES category(id)
        )
        """)
        self.conn.commit()

       

        if "first_name" not in cols:
            self.cur.execute("ALTER TABLE user ADD COLUMN first_name TEXT")

        if "last_name" not in cols:
            self.cur.execute("ALTER TABLE user ADD COLUMN last_name TEXT")

        if "phone_number" not in cols:
            self.cur.execute("ALTER TABLE user ADD COLUMN phone_number TEXT")

        self.conn.commit()


    def create_user(self, chat_id):
        self.cur.execute(  "INSERT OR IGNORE INTO user(chat_id) VALUES (?)", (chat_id,))
        self.conn.commit()



    def update_user_data(self, chat_id, key, value):
        self.cur.execute(f"""update user set {key} = ? where chat_id = ?""", (value, chat_id))
        self.conn.commit()



    def get_user_by_chat_id(self, chat_id):
        self.cur.execute("SELECT * FROM user WHERE chat_id = ?", (chat_id,))
        row = self.cur.fetchone()

        if row is None:
            return None

        columns = [col[0] for col in self.cur.description]
        return dict(zip(columns, row))



    def get_categories_by_parent(self, parent_id=None):
        self.cur.execute(
            "SELECT * FROM category WHERE parent_id IS ?",
            (parent_id,)
        )
        rows = self.cur.fetchall()

        columns = [col[0] for col in self.cur.description]
        return [dict(zip(columns, row)) for row in rows]



    def get_category_parent(self, category_id):
        self.cur.execute("""select parent_id from category where id = ?""", (category_id, ))
        category = dict_fetchone(self.cur)
        return category


######### new ##############
    def get_products_by_category(self, category_id):
        self.cur.execute("""select * from product where category_id = ?""", (category_id, ))
        products = dict_fetchall(self.cur)
        return products

    def get_product_by_id(self, product_id):
        self.cur.execute("""select * from product where id = ?""", (product_id, ))
        product = dict_fetchone(self.cur)
        return product


# lesson-4 ####################

    def get_product_for_cart(self, product_id):
        self.cur.execute(
            """select product.*, category.name_uz as cat_name_uz, category.name_ru as cat_name_ru 
            from product inner join category on product.category_id = category.id where product.id = ?""",
            (product_id, )
        )
        product = dict_fetchone(self.cur)
        return product

    def create_order(self, user_id, products, payment_type, location):
        self.cur.execute(
            """insert into "order"(user_id, status, payment_type, longitude, latitude, created_at) values (?, ?, ?, ?, ?, ?)""",
            (user_id, 1, payment_type, location.longitude, location.latitude, datetime.now())
        )
        self.conn.commit()
        self.cur.execute(
            """select max(id) as last_order from "order" where user_id = ?""", (user_id, )
        )
        last_order = dict_fetchone(self.cur)['last_order']
        for key, val in products.items():
            self.cur.execute(
                """insert into "order_product"(product_id, order_id, amount, created_at) values (?, ?, ?, ?)""",
                (int(key), last_order,  int(val), datetime.now())
            )
        self.conn.commit()

    def get_user_orders(self, user_id):
        self.cur.execute(
            """select * from "order" where user_id = ? and status = 1""", (user_id, )
        )
        orders = dict_fetchall(self.cur)
        return orders

    def get_order_products(self, order_id):
        self.cur.execute(
            """select order_product.*, product.name_uz as product_name_uz, product.name_ru as product_name_ru, 
            product.price as product_price from order_product inner join product on order_product.product_id = product.id
            where order_id = ?""", (order_id, ))
        products = dict_fetchall(self.cur)
        return products

#****************************************************************************************************

def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
