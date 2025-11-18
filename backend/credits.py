from backend.models import db, Designer
from backend.email_utils import send_out_of_credits_email


# ---------------------------------------------------------
# Check if designer has credits
# ---------------------------------------------------------
def has_credits(designer_id):
    designer = Designer.query.get(designer_id)
    if not designer:
        return False
    return designer.credits > 0


# ---------------------------------------------------------
# Deduct credit for a rematch
# ---------------------------------------------------------
def deduct_credit(designer_id):
    designer = Designer.query.get(designer_id)
    if not designer:
        return False

    if designer.credits <= 0:
        # send out-of-credits email
        send_out_of_credits_email(designer.email)
        return False

    designer.credits -= 1
    db.session.commit()
    return True


# ---------------------------------------------------------
# Add credits (Stripe, future purchases)
# ---------------------------------------------------------
def add_credits(designer_id, amount):
    designer = Designer.query.get(designer_id)
    if not designer:
        return False

    designer.credits += amount
    db.session.commit()
    return True
