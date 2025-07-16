from app import db

class Message(db.Model):
    __tablename__ = "Message"
    id = db.Column(db.Integer, primary_key=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    sender_user = db.relationship("User", back_populates="messages")
    offer_id = db.Column(db.Integer, db.ForeignKey("Offer.id"))
    offer = db.relationship("Offer", back_populates="messages")
    text = db.Column(db.String(300))

    def dict(self):
        return {
            "id": self.id,
            "sender_user_id": self.sender_user_id,
            "offer_id": self.offer_id,
            "text": self.text
        }