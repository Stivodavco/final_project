from app import db

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(300))
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(255))
    offers = db.relationship("Offer", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")
    messages = db.relationship("Message", back_populates="sender_user")

    def dict(self):
        offers_dict = []
        reviews_dict = []
        messages_dict = []

        for offer in self.offers:
            offers_dict.append(offer.dict())

        for review in self.reviews:
            reviews_dict.append(review.dict())

        for message in self.messages:
            messages_dict.append(message.dict())

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "username": self.username,
            "password": self.password,
            "offers": offers_dict,
            "reviews": reviews_dict,
            "messages": messages_dict
        }