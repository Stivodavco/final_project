from app import db

class Review(db.Model):
    __tablename__ = "Review"
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    recipient = db.relationship("User", foreign_keys=[recipient_id],back_populates="reviews")
    sender_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    sender = db.relationship("User", foreign_keys=[sender_id],back_populates="sent_reviews")
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(300))

    def dict(self):
        return {
            "id": self.id,
            "recipient_id": self.recipient_id,
            "sender_id": self.sender_id,
            "rating": self.rating,
            "comment": self.comment
        }