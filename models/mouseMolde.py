Mouse {
    "id": db.Column(db.Integer, primary_key=True),
    "name": db.Column(db.String(80), nullable=False),
    "sex": db.Column(db.String(10), nullable=False),
    "birth_date": db.Column(db.DateTime),
    "genotype": db.Column(db.String(100)),
    "phenotype": db.Column(db.String(100)),
    "notes": db.Column(db.Text),
    "health_status": db.Column(db.String(50), nullable=False, default="healthy"),

}