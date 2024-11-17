from database import db

test_collection = db['test_collection']

# Insert a test document
test_collection.insert_one({"message": "Hello from MongoDB!"})

# Retrieve and print the document
document = test_collection.find_one({"message": "Hello from MongoDB!"})
print(document)