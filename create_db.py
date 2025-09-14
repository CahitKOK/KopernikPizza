from app import app
from extensions import db
import models  # önemli: modelleri import etmeliyiz ki tabloları bilsin

with app.app_context():
    db.create_all()
    print("✅ Tables created:", db.metadata.tables.keys())
