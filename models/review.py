from app import db

class Review(db.Model):
    __tablename__ = "Review"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    user = db.relationship("User", back_populates="reviews")
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(300))

    def dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment
        }