"""
name: mary laro
date: september 30, 2026
assignment: 4.5 performance assessment - python application accessing a graph database
purpose: connect to a local neo4j database, import and parse the amazon json dataset 
         from desktop path to create category, product, review, and reviewer nodes and relationships, 
         and provide an interactive menu allowing the user to perform crud operations.
"""

import json
import os
from neo4j import GraphDatabase

# database connection configuration
uri = "neo4j://127.0.0.1:7687"
auth = ("neo4j", "password1")

# file path setup using the desktop working folder
folder_path = r"C:\Users\Student\Desktop\Neo4j"
primary_file = os.path.join(folder_path, "dataset_en_dev.json")
fallback_file = os.path.join(folder_path, "amazon.json")

if os.path.exists(primary_file):
    json_file = primary_file
elif os.path.exists(fallback_file):
    json_file = fallback_file
else:
    json_file = "dataset_en_dev.json"


class reviewgraphapp:
    def __init__(self, uri_conn, auth_conn):
        self.driver = GraphDatabase.driver(uri_conn, auth=auth_conn)

    def close(self):
        self.driver.close()

    # --- initial data import functions ---

    def import_json_data(self, filepath):
        """loads json data from file."""
        with open(filepath, "r", encoding="utf-8") as a:
            return json.load(a)

    def create_category_nodes(self, data):
        """*create category labeled nodes from the imported json data."""
        query = """
        unwind $categories as a
        merge (:Category {name: a})
        """
        categories = set()
        for b in data:
            if "category" in b and b["category"]:
                categories.add(b["category"])
            elif "product_category" in b and b["product_category"]:
                categories.add(b["product_category"])

        with self.driver.session() as c:
            c.run(query, categories=list(categories))

    def create_product_nodes(self, data):
        """*create product labeled nodes from the imported json data."""
        query = """
        unwind $products as a
        merge (:Product {name: a})
        """
        products = set()
        for b in data:
            if "product_id" in b:
                products.add(b["product_id"])
            elif "product" in b:
                products.add(b["product"])

        with self.driver.session() as c:
            c.run(query, products=list(products))

    def create_review_nodes(self, data):
        """*create review labeled nodes from the imported json data."""
        query = """
        unwind $reviews as a
        create (:Review {
            id: a.id,
            title: a.title,
            content: a.content,
            stars: a.stars
        })
        """
        reviews = []
        for b, c in enumerate(data):
            review_item = {
                "id": c.get("review_id", str(b)),
                "title": c.get("review_title", c.get("title", "")),
                "content": c.get("review_body", c.get("content", "")),
                "stars": float(c.get("stars", c.get("star_rating", 0.0)))
            }
            reviews.append(review_item)

        with self.driver.session() as d:
            d.run(query, reviews=reviews)

    def create_reviewer_nodes(self, data):
        """*create reviewer labeled nodes from the imported json data."""
        query = """
        unwind $reviewers as a
        merge (:Reviewer {name: a})
        """
        reviewers = set()
        for b in data:
            if "reviewer_id" in b:
                reviewers.add(b["reviewer_id"])
            elif "reviewer" in b:
                reviewers.add(b["reviewer"])

        with self.driver.session() as c:
            c.run(query, reviewers=list(reviewers))

    def connect_products_to_categories(self, data):
        """*create a relationship between product nodes and category nodes."""
        query = """
        unwind $pairs as a
        match (b:Product {name: a.product})
        match (c:Category {name: a.category})
        merge (b)-[:IN_CATEGORY]->(c)
        """
        pairs = []
        for d in data:
            prod = d.get("product_id", d.get("product"))
            cat = d.get("category", d.get("product_category"))
            if prod and cat:
                pairs.append({"product": prod, "category": cat})

        with self.driver.session() as e:
            e.run(query, pairs=pairs)

    def connect_reviews_to_reviewers(self, data):
        """*create a relationship between reviewer nodes and review nodes."""
        query = """
        unwind $pairs as a
        match (b:Reviewer {name: a.reviewer})
        match (c:Review {id: a.review_id})
        merge (b)-[:WROTE]->(c)
        """
        pairs = []
        for d, e in enumerate(data):
            reviewer = e.get("reviewer_id", e.get("reviewer"))
            review_id = e.get("review_id", str(d))
            if reviewer:
                pairs.append({"reviewer": reviewer, "review_id": review_id})

        with self.driver.session() as f:
            f.run(query, pairs=pairs)

    def connect_reviews_to_products(self, data):
        """*create a relationship between product nodes and review nodes."""
        query = """
        unwind $pairs as a
        match (b:Product {name: a.product})
        match (c:Review {id: a.review_id})
        merge (c)-[:REVIEWS]->(b)
        """
        pairs = []
        for d, e in enumerate(data):
            prod = e.get("product_id", e.get("product"))
            review_id = e.get("review_id", str(d))
            if prod:
                pairs.append({"product": prod, "review_id": review_id})

        with self.driver.session() as f:
            f.run(query, pairs=pairs)

    # --- interactive menu operations ---

    def create_custom_node(self, label, name, extra_props=None):
        """*allow the user to create their own node with category, product, review, or reviewer label."""
        if extra_props is None:
            extra_props = {}

        with self.driver.session() as a:
            if label in ["Category", "Product", "Reviewer"]:
                query = f"create (b:{label} {{name: $name}})"
                a.run(query, name=name)
            elif label == "Review":
                query = """
                create (b:Review {
                    title: $title,
                    content: $content,
                    stars: $stars
                })
                """
                a.run(query, **extra_props)

    def create_custom_relationship(self, rel_type_option, from_node, to_node, rel_name):
        """*allow the user to create their own relationship between product and category nodes, or product and review nodes."""
        with self.driver.session() as a:
            if rel_type_option == "1":
                query = f"""
                match (b:Product {{name: $from_node}})
                match (c:Category {{name: $to_node}})
                create (b)-[:`{rel_name}`]->(c)
                """
                a.run(query, from_node=from_node, to_node=to_node)
            elif rel_type_option == "2":
                query = f"""
                match (b:Product {{name: $from_node}})
                match (c:Review)
                where c.title = $to_node or c.id =$to_node
                create (b)-[:`{rel_name}`]->(c)
                """
                a.run(query, from_node=from_node, to_node=to_node)

    def count_products_per_category(self, category_name):
        """*allow the user to enter a category name and see the count of product nodes related to it."""
        query = """
        match (a:Product)-[]-(b:Category {name: $category_name})
        return count(distinct a) as product_count
        """
        with self.driver.session() as c:
            result = c.run(query, category_name=category_name)
            record = result.single()
            return record["product_count"] if record else 0

    def count_reviews_per_reviewer(self, reviewer_name):
        """*allow the user to enter a reviewer name (reviewer_id) and see the count of review nodes related to it."""
        query = """
        match (a:Reviewer {name: $reviewer_name})-[]-(b:Review)
        return count(distinct b) as review_count
        """
        with self.driver.session() as c:
            result = c.run(query, reviewer_name=reviewer_name)
            record = result.single()
            return record["review_count"] if record else 0

    def delete_category(self, category_name):
        """*allow the user to enter a category name and delete the associated category node."""
        query = """
        match (a:Category {name: $category_name})
        detach delete a
        """
        with self.driver.session() as b:
            b.run(query, category_name=category_name)

    def delete_all_relationships(self):
        """*delete all relationships in the graph."""
        query = """
        match ()-[a]->()
        delete a
        """
        with self.driver.session() as b:
            b.run(query)

    def delete_all_nodes(self):
        """*delete all nodes in the graph."""
        query = """
        match (a)
        detach delete a
        """
        with self.driver.session() as b:
            b.run(query)


def main():
    print("Connecting to local Neo4j database...")
    app = reviewgraphapp(uri, auth)

    try:
        print("Importing data from file...")
        data = app.import_json_data(json_file)

        print("Creating Category nodes...")
        app.create_category_nodes(data)

        print("Creating Product nodes...")
        app.create_product_nodes(data)

        print("Creating Review nodes...")
        app.create_review_nodes(data)

        print("Creating Reviewer nodes...")
        app.create_reviewer_nodes(data)

        print("Connecting Products to Categories...")
        app.connect_products_to_categories(data)

        print("Connecting Reviews to Reviewers...")
        app.connect_reviews_to_reviewers(data)

        print("Connecting Reviews to Products...")
        app.connect_reviews_to_products(data)
    except Exception as a:
        print(f"Note on data loading: {a}")

    while True:
        print("\nType in a number and press enter to execute the menu option.")
        print("1. Create a new node")
        print("2. Create a new relationship")
        print("3. Count Products per Category")
        print("4. Count Reviews per Reviewer")
        print("5. Delete a category")
        print("6. Delete all relationships")
        print("7. Delete all nodes")
        print("8. Exit the program")

        choice = input().strip()

        if choice == "1":
            print("What kind of node do you want to create?")
            print("1. Category")
            print("2. Product")
            print("3. Review")
            print("4. Reviewer")
            node_choice = input().strip()

            if node_choice == "1":
                cat_name = input("Enter the name of the new category:\n").strip()
                app.create_custom_node("Category", cat_name)
                print("\nNode Created!")
            elif node_choice == "2":
                prod_name = input("Enter the name of the new product:\n").strip()
                app.create_custom_node("Product", prod_name)
                print("\nNode Created!")
            elif node_choice == "3":
                title = input("Enter the title of the review:\n").strip()
                content = input("Enter the content of the review:\n").strip()
                stars = float(input("Enter the star rating (number):\n").strip())
                app.create_custom_node("Review", "", {"title": title, "content": content, "stars": stars})
                print("\nNode Created!")
            elif node_choice == "4":
                rev_name = input("Enter the name of the reviewer:\n").strip()
                app.create_custom_node("Reviewer", rev_name)
                print("\nNode Created!")

        elif choice == "2":
            print("What kind of relationship do you want to create?")
            print("1. Product to Category")
            print("2. Product to Review")
            rel_choice = input().strip()

            if rel_choice == "1":
                prod_name = input("Enter the name of the Product to connect:\n").strip()
                cat_name = input("Enter the name of the Category to connect:\n").strip()
                rel_name = input("Enter the name of the Relationship:\n").strip()
                app.create_custom_relationship("1", prod_name, cat_name, rel_name)
                print("\nRelationship Created!")
            elif rel_choice == "2":
                prod_name = input("Enter the name of the Product to connect:\n").strip()
                review_name = input("Enter the title/id of the Review to connect:\n").strip()
                rel_name = input("Enter the name of the Relationship:\n").strip()
                app.create_custom_relationship("2", prod_name, review_name, rel_name)
                print("\nRelationship Created!")

        elif choice == "3":
            category_name = input("Enter the name of the category to count the products of:\n").strip()
            count = app.count_products_per_category(category_name)
            print(f"{category_name} has [{count}] products!")

        elif choice == "4":
            reviewer_name = input("Enter the name of the reviewer to count the reviews of:\n").strip()
            count = app.count_reviews_per_reviewer(reviewer_name)
            print(f"{reviewer_name} has written [{count}] reviews!")

        elif choice == "5":
            category_name = input("Enter the name of the category to remove:\n").strip()
            app.delete_category(category_name)
            print(f"{category_name} removed.")

        elif choice == "6":
            app.delete_all_relationships()
            print("All relationships removed.")

        elif choice == "7":
            app.delete_all_nodes()
            print("All nodes removed.")

        elif choice == "8":
            app.close()
            break


if __name__ == "__main__":
    main()
