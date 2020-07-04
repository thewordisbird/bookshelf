from bookshelf import firebase
"""
Functions to update duplicated data in firestore database. 

Eventually replace with cloud functions
"""
firestore = firebase.firestore()

def update_user_data_in_books(uid, update_data):
    """Update display_name and photo_url in book documents"""
    valid_update_fields = {'display_name', 'photo_url'}
    valid_update_data = {k:v for k,v in update_data.items() if k in valid_update_fields}
    if valid_update_fields:
        books = firestore.get_collection(f"users/{uid}/books")
        
        for book in books:
            #print(f"Updating {book['title']} with {update_data}")
            firestore.update_document(f"users/{uid}/books/{book['bid']}", update_data)



