# name: mary laro
# date: september 22, 2026
# assignment: 3.5 performance assessment - python application accessing a column family database
# purpose: connect to a cassandra database to manage keyspaces and tables, import json review data, execute cql queries, alter schema, and query review statistics through an interactive menu.

import json
import os
from cassandra.cluster import Cluster


def main():
    # connect to the cassandra cluster
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()

    # *create a new keyspace in the cassandra database named amazon
    session.execute(
        """
        create keyspace if not exists amazon 
        with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """
    )
    session.set_keyspace("amazon")

    # *create a new table in the cassandra database named reviews
    session.execute(
        """
        create table if not exists reviews (
            review_id text,
            product_id text,
            reviewer_id text,
            stars int,
            review_body text,
            review_title text,
            product_category text,
            primary key (product_category, review_id)
        );
    """
    )

    # *create a new table in the cassandra database named productcategories
    session.execute(
        """
        create table if not exists productcategories (
            product_category text,
            product_id text,
            stars int,
            language text,
            primary key (product_category, product_id)
        );
    """
    )

    # create secondary indexes for filtering
    session.execute(
        "create index if not exists idx_reviews_stars on reviews (stars);"
    )
    session.execute(
        "create index if not exists idx_prodcat_stars on productcategories (stars);"
    )

    # *insert data from the json file into reviews and productcategories tables
    json_candidates = [
        "amazon_reviews.json",
        "reviews.json",
        "dataset.json",
        "amazon.json",
    ]
    json_path = None
    for filename in json_candidates:
        if os.path.exists(filename):
            json_path = filename
            break

    if json_path is None:
        for file in os.listdir("."):
            if file.endswith(".json"):
                json_path = file
                break

    if json_path and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                f.seek(0)
                data = [json.loads(line) for line in f if line.strip()]

        for item in data:
            review_id = str(item.get("review_id", ""))
            product_id = str(item.get("product_id", ""))
            reviewer_id = str(item.get("reviewer_id", ""))
            stars = int(item.get("stars", item.get("star_rating", 0)))
            review_body = str(item.get("review_body", ""))
            review_title = str(item.get("review_title", ""))
            product_category = str(
                item.get("product_category", item.get("category", ""))
            )
            language = str(item.get("language", "en"))

            session.execute(
                """
                insert into reviews (review_id, product_id, reviewer_id, stars, review_body, review_title, product_category)
                values (%s, %s, %s, %s, %s, %s, %s);
            """,
                (
                    review_id,
                    product_id,
                    reviewer_id,
                    stars,
                    review_body,
                    review_title,
                    product_category,
                ),
            )

            session.execute(
                """
                insert into productcategories (product_id, stars, language, product_category)
                values (%s, %s, %s, %s);
            """,
                (product_id, stars, language, product_category),
            )

    # interactive menu loop
    while True:
        print("\nType in a number and press enter to execute the menu option.")
        print("1. Display product category list")
        print("2. Display high (4+) star review count")
        print("3. Display low (1) star review count")
        print("4. Enter a query")
        print("5. Add/Remove table columns")
        print("6. Delete tables")
        print("7. Delete keyspace")
        print("8. Exit the program")

        choice = input().strip()

        if choice == "1":
            # *display all distinct product categories from the productcategories table
            rows = session.execute(
                "select distinct product_category as category from productcategories;"
            )
            print("\nProduct Category List:")
            for row in rows:
                print(row)

        elif choice == "2":
            # *display the count of 4-star and higher reviews for a user-entered product category
            cat = input("Enter product category: ").strip()
            query = "select count(*) from reviews where product_category = %s and stars >= 4 allow filtering;"
            count = session.execute(query, (cat,)).one()[0]
            print(f"4+ star reviews for {cat}: {count}")

        elif choice == "3":
            # *display the count of 1-star reviews for a user-entered product category
            cat = input("Enter product category: ").strip()
            query = "select count(*) from reviews where product_category = %s and stars = 1 allow filtering;"
            count = session.execute(query, (cat,)).one()[0]
            print(f"1-star reviews for {cat}: {count}")

        elif choice == "4":
            # *allow the user to type in and execute cql select statements
            user_query = input("Enter CQL SELECT statement: ").strip()
            try:
                results = session.execute(user_query)
                for r in results:
                    print(r)
            except Exception as e:
                print("Error executing query:", e)

        elif choice == "5":
            # *allow the user to add and remove columns from the reviews and productcategories tables
            table = input(
                "Enter table name (reviews or productcategories): "
            ).strip()
            action = input("Enter action (add or drop): ").strip().lower()
            col_name = input("Enter column name: ").strip()

            if action == "add":
                data_type = input(
                    "Enter data type (e.g., text, int): "
                ).strip()
                sql = f"alter table {table} add {col_name} {data_type};"
            else:
                sql = f"alter table {table} drop {col_name};"

            try:
                session.execute(sql)
                print(f"Column {col_name} successfully updated on {table}.")
            except Exception as e:
                print("Error altering column:", e)

        elif choice == "6":
            # *allow the user to delete the reviews and productcategories tables
            session.execute("drop table if exists reviews;")
            session.execute("drop table if exists productcategories;")
            print("Reviews and ProductCategories tables deleted.")

        elif choice == "7":
            # *allow the user to delete the amazon keyspace
            session.execute("drop keyspace if exists amazon;")
            print("Amazon keyspace deleted.")

        elif choice == "8":
            print("Exiting program.")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 8.")

    cluster.shutdown()


if __name__ == "__main__":
    main()
