from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(300))
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(255))
    offers = db.relationship("Offer", foreign_keys="Offer.user_id", back_populates="user")
    reviews = db.relationship("Review", foreign_keys="Review.recipient_id",back_populates="recipient")
    sent_reviews = db.relationship("Review", foreign_keys="Review.sender_id",back_populates="sender")
    interests = db.relationship("Offer", foreign_keys="Offer.interested_user_id",back_populates="interested_user")
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

    def get_rating(self):
        total_stars = 0

        for review in self.reviews:
            total_stars += review.rating

        reviews_num = len(self.reviews)

        if reviews_num < 1:
            return 0.0, 0
        else:
            return round(total_stars/reviews_num,1), reviews_num