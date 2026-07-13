_author__ = "Kailine Lima"
__version__ = "1.0.0"


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    facility_id = db.Column(db.Integer, db.ForeignKey("facility.id"), nullable=False)
