# ==============================================================================
# Name: Mary Laro
# Date: September 21, 2026
# Assignment: 2.5 Performance Assessment - Python Application Accessing a Document Database
# Purpose: This program performs CRUD (Create, Read, Update, Delete) operations 
#          on a MongoDB database named 'Amazon' and collection 'ReviewData' using PyMongo.
# ==============================================================================

import pymongo
import re

# Connect to the local MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Amazon"]
collection = db["ReviewData"]

print("Connecting to local Mongo database...")
print("Connected successfully!\n")


def query_menu():
    """Sub-menu for retrieving documents using find_one and find with filters."""
    while True:
        print("\nPlease type in a number and press enter to execute the menu option")
        print("1. Query by reviewID")
        print("2. Filter for a number of stars and greater")
        print("3. Filter for less than a number of stars")
        print("4. Filter for a word in the title")
        print("5. Filter for a word in the review body content")
        print("6. Return to Main Menu")

        sub_choice = input("Enter choice (1-6): ").strip()

        # *Retrieve documents using the .find_one() function
        if sub_choice == "1":
            review_id = input("\nEnter reviewID to search for: ").strip()
            # Searching by review_id string
            doc = collection.find_one({"review_id": review_id})
            if doc:
                print(doc)
            else:
                print("No document found with that reviewID.")

        # *Retrieve documents filtering for greater than or equal to stars
        elif sub_choice == "2":
            stars_input = input("\nEnter minimum star rating (e.g., 3): ").strip()
            try:
                # Handle cases where stars might be stored as strings or numbers in MongoDB
                query = {
                    "$or": [
                        {"stars": {"$gte": int(stars_input)}},
                        {"stars": {"$gte": str(stars_input)}}
                    ]
                }
                results = collection.find(query)
                found = False
                for item in results:
                    found = True
                    print(item)
                if not found:
                    print("No reviews found matching that criteria.")
            except ValueError:
                print("Please enter a valid numeric value.")

        # *Retrieve documents filtering for less than stars
        elif sub_choice == "3":
            stars_input = input("\nEnter star rating threshold (less than): ").strip()
            try:
                query = {
                    "$or": [
                        {"stars": {"$lt": int(stars_input)}},
                        {"stars": {"$lt": str(stars_input)}}
                    ]
                }
                results = collection.find(query)
                found = False
                for item in results:
                    found = True
                    print(item)
                if not found:
                    print("No reviews found matching that criteria.")
            except ValueError:
                print("Please enter a valid numeric value.")

        # *Retrieve documents filtering for a word within review_title
        elif sub_choice == "4":
            word = input("\nSearch the title for:\n").strip()
            # Case-insensitive regex match
            query = {"review_title": {"$regex": re.escape(word), "$options": "i"}}
            results = collection.find(query)
            found = False
            for item in results:
                found = True
                print(item)
            if not found:
                print(f"No reviews found with '{word}' in the title.")

        # *Retrieve documents filtering for a word within review_body
        elif sub_choice == "5":
            word = input("\nSearch the review body for:\n").strip()
            query = {"review_body": {"$regex": re.escape(word), "$options": "i"}}
            results = collection.find(query)
            found = False
            for item in results:
                found = True
                print(item)
            if not found:
                print(f"No reviews found with '{word}' in the body.")

        elif sub_choice == "6":
            break
        else:
            print("Invalid selection. Please try again.")


def add_document():
    """*Create a new document in the Amazon database in the ReviewData collection."""
    print("\n--- Add a New Review Document ---")
    review_id = input("Enter review_id: ").strip()
    product_id = input("Enter product_id: ").strip()
    reviewer_id = input("Enter reviewer_id: ").strip()
    stars = input("Enter stars (1-5): ").strip()
    review_body = input("Enter review_body: ").strip()
    review_title = input("Enter review_title: ").strip()
    language = input("Enter language: ").strip()
    product_category = input("Enter product_category: ").strip()

    new_doc = {
        "review_id": review_id,
        "product_id": product_id,
        "reviewer_id": reviewer_id,
        "stars": stars,
        "review_body": review_body,
        "review_title": review_title,
        "language": language,
        "product_category": product_category
    }

    result = collection.insert_one(new_doc)
    print(f"\nDocument inserted successfully with _id: {result.inserted_id}")


def update_document():
    """*Allow the user to enter a field and update the value within a document."""
    print("\n--- Update Document Field ---")
    review_id = input("Enter the review_id of the document to update: ").strip()
    
    # Verify existence first
    existing = collection.find_one({"review_id": review_id})
    if not existing:
        print("No document found with that review_id.")
        return

    field_to_update = input("Enter field name to update (e.g., review_title, stars): ").strip()
    new_value = input(f"Enter new value for '{field_to_update}': ").strip()

    update_result = collection.update_one(
        {"review_id": review_id},
        {"$set": {field_to_update: new_value}}
    )

    if update_result.modified_count > 0:
        print("Document updated successfully!")
    else:
        print("Document found, but no changes were made.")


def delete_single_document():
    """*Allow the user to enter a document ID and delete a specific document."""
    print("\n--- Delete a Document ---")
    review_id = input("Enter the review_id of the document to delete: ").strip()
    
    result = collection.delete_one({"review_id": review_id})
    if result.deleted_count > 0:
        print(f"Document with review_id '{review_id}' deleted successfully.")
    else:
        print("No document found matching that review_id.")


def delete_all_documents():
    """*Menu option to remove all documents in a collection."""
    confirm = input("\nAre you sure you want to delete ALL documents in the collection? (y/n): ").strip().lower()
    if confirm == 'y':
        result = collection.delete_many({})
        print(f"Deleted {result.deleted_count} documents from ReviewData.")
    else:
        print("Operation cancelled.")


def delete_collection():
    """*Menu option to delete the collection from the Amazon database."""
    confirm = input("\nAre you sure you want to DROP the 'ReviewData' collection? (y/n): ").strip().lower()
    if confirm == 'y':
        collection.drop()
        print("Collection 'ReviewData' has been deleted.")
    else:
        print("Operation cancelled.")


def main():
    """Main menu loop driven by user options matching assignment specifications."""
    while True:
        print("\nType in a number and press enter to execute the menu option.")
        print("1. Query for documents")
        print("2. Add a new document")
        print("3. Update fields of a document")
        print("4. Delete a document")
        print("5. Delete all documents from the collection")
        print("6. Delete a collection")
        print("7. Exit the program")

        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            query_menu()
        elif choice == "2":
            add_document()
        elif choice == "3":
            update_document()
        elif choice == "4":
            delete_single_document()
        elif choice == "5":
            delete_all_documents()
        elif choice == "6":
            delete_collection()
        elif choice == "7":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("Invalid menu selection. Please try again.")


if __name__ == "__main__":
    main()
