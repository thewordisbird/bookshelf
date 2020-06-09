from firebase_admin import firestore

def add_user(user, user_id=None):
    # Take User object
    db = firestore.client()
    user_ref = db.collection('users').document(user_id)
    user_ref.set(user)
    