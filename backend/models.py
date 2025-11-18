from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------------------
# Designer Model
# -------------------------------
class Designer(db.Model):
    __tablename__ = 'designers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    skills = db.Column(db.String(300))
    experience = db.Column(db.String(200))

    credits = db.Column(db.Integer, default=3)  # rematch credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship("Match", backref="designer", lazy=True)

    def __repr__(self):
        return f"<Designer {self.name}>"


# -------------------------------
# Founder Model
# -------------------------------
class Founder(db.Model):
    __tablename__ = 'founders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    project = db.Column(db.Text)
    needs = db.Column(db.String(300))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    matches = db.relationship("Match", backref="founder", lazy=True)

    def __repr__(self):
        return f"<Founder {self.name}>"


# -------------------------------
# Match Model
# -------------------------------
class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey('designers.id'))
    founder_id = db.Column(db.Integer, db.ForeignKey('founders.id'))

    status = db.Column(db.String(20), default="pending")
    # statuses: pending • confirmed • rejected

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Match D{self.designer_id} - F{self.founder_id}>"


# -------------------------------
# Credit Purchase Log
# -------------------------------
class CreditPurchase(db.Model):
    __tablename__ = 'credit_purchases'

    id = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey('designers.id'))
    credits_added = db.Column(db.Integer, default=1)
    amount = db.Column(db.Integer)  # in cents from Stripe
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Credits +{self.credits_added} to Designer {self.designer_id}>"
