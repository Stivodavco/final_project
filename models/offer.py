from app import db

class Offer(db.Model):
    __tablename__ = "Offer"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    user = db.relationship("User", back_populates="offers")
    messages = db.relationship("Message", back_populates="offer")
    price = db.Column(db.Integer)

    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "price": self.price
        }