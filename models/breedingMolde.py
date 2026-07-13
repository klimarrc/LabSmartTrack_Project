

BreedingPair = {
    "id": db.Column(db.Integer, primary_key=True),
    "dam_id": db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=False),
    "sire_id": db.Column(db.Integer, db.ForeignKey("mouse.id"), nullable=False),
    "status": db.Column(db.String(40), nullable=False, default="active"),
    "start_date": db.Column(db.DateTime, nullable=False, default=datetime.utcnow),
    "end_date": db.Column(db.DateTime),
    "notes": db.Column(db.Text),
    "created_at": db.Column(db.DateTime, nullable=False, default=datetime.utcnow),
    "dam": db.relationship("Mouse", foreign_keys=[dam_id], backref="breeding_pairs_as_dam"),
    "sire": db.relationship("Mouse", foreign_keys=[sire_id], backref="breeding_pairs_as_sire"),
    "litter": db.relationship("Litter", backref="breeding_pair", lazy=True)
}