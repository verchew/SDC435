# Name: Mary Laro
# Date: September 16, 2026
# Assignment: 1.8 PA
# Purpose: Python application to perform interactive CRUD operations on sets in a Redis database.

import redis

# Establish connection to local Redis database
r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

def main_menu():
    while True:
        print("Type in a number and press enter to execute the menu option.")
        print("1. Query for set members")
        print("2. Add a new set")
        print("3. Update members of a set")
        print("4. Delete a set")
        print("5. Delete all data from the database")
        print("6. Exit the program")
        
        choice = input()

        # *Retrieve the members of a specific set from the Redis database.
        if choice == '1':
            key = input("\nEnter the key of the set you wish to query:\n")
            if r.exists(key):
                print("Members of set '{}':".format(key))
                members = r.smembers(key)
                for member in members:
                    print(member)
            else:
                print("Set '{}' does not exist.\n".format(key))

        # *Create a new set in the Redis database.
        elif choice == '2':
            key = input("\nEnter the key you wish to add:\n")
            num_members = int(input("\nEnter how many members will this set have:\n"))
            for _ in range(num_members):
                val = input("\nEnter the next member value:\n")
                r.sadd(key, val)
            print()

        # *Update the members of a specific set in the Redis database.
        elif choice == '3':
            key = input("\nEnter the key of the set you wish to update:\n")
            update_menu(key)

        # *Delete a specific set from the Redis database.
        elif choice == '4':
            key = input("\nEnter the key of the set you wish to delete:\n")
            r.delete(key)
            print("Set '{}' deleted.\n".format(key))

        # *Delete all data from the Redis database.
        elif choice == '5':
            r.flushdb()
            print("All data deleted from the database.\n")

        elif choice == '6':
            break

def update_menu(key):
    while True:
        print("\nPlease type in a number and press enter to execute the menu option")
        print("1. Add new member")
        print("2. Remove member")
        print("3. Remove all members")
        print("4. Exit Update Menu")
        
        sub_choice = input()

        if sub_choice == '1':
            val = input("\nEnter member value to add:\n")
            r.sadd(key, val)
            print("Member added.")

        elif sub_choice == '2':
            val = input("\nEnter member value to remove:\n")
            r.srem(key, val)
            print("Member removed.")

        elif sub_choice == '3':
            print("\nRemoving all set members...")
            while r.scard(key) > 0:
                print("Removing Member: {}...".format(r.spop(key)))
            print("\nThe cardinality of the set is now:")
            print(r.scard(key))

        elif sub_choice == '4':
            print()
            break

if __name__ == "__main__":
    main_menu()
