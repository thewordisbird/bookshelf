from bookshelf import firebase

"""Functions to update duplicated data in firestore database.

Eventually replace with cloud functions.

TODO: Testing.
"""
firestore = firebase.firestore()


def update_user_data_in_books(uid, update_data):
    """Update display_name and photo_url in book documents

    Args:
        uid (str): User Id.
        update_data (dict): Data to be updated

    TODO: Update User Data.
    """
    valid_update_fields = {"display_name", "photo_url"}
    # valid_update_data = {
    #     k: v for k, v in update_data.items() if k in valid_update_fields
    # }
    if valid_update_fields:
        books = firestore.get_collection(f"users/{uid}/books")

        for book in books:
            firestore.update_document(f"users/{uid}/books/{book['bid']}", update_data)


def thumbnail_url_to_https():
    """Convert Book cover URl to https."""
    # NEED DOCUMENT PATH TO UPDATE
    users = firestore.get_collection("users")
    for user in users:
        # print(f"Updating https for {user['display_name']}")
        books = firestore.get_collection(f"users/{user['doc_id']}/books")
        for book in books:
            # print(f"\t{book['title']}")
            if "cover_url" in book:
                if book["cover_url"][4] != "s":
                    https_url = book["cover_url"][:4] + "s" + book["cover_url"][4:]
                    firestore.update_document(
                        f"users/{user['doc_id']}/books/{book['bid']}",
                        {"cover_url": https_url},
                    )
