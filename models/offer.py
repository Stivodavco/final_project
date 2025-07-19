from app import db

class Offer(db.Model):
    __tablename__ = "Offer"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    user = db.relationship("User", foreign_keys=[user_id],back_populates="offers")
    interested_user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    interested_user = db.relationship("User", foreign_keys=[interested_user_id],back_populates="interests")
    messages = db.relationship("Message", back_populates="offer")
    price = db.Column(db.Integer)

    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "interested_user_id": self.interested_user_id,
            "description": self.description,
            "price": self.price
        }