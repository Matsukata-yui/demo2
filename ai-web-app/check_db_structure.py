from app import create_app, db
from app.models import CollectedData, DeepCollectionData

app = create_app()

with app.app_context():
    print('CollectedData columns:', [column.name for column in CollectedData.__table__.columns])
    print('DeepCollectionData columns:', [column.name for column in DeepCollectionData.__table__.columns])
