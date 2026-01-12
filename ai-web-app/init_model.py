
from app import create_app, db
from app.models import ModelConfig
from app.config import Config

app = create_app()

with app.app_context():
    # Check if any model exists
    model = ModelConfig.query.first()
    if not model:
        print("Creating default model config...")
        new_model = ModelConfig(
            name="Default Model",
            api_url=Config.AI_API_URL,
            api_key=Config.AI_API_KEY,
            model_name=Config.AI_MODEL_NAME,
            enabled=True
        )
        # Encrypt the API key
        new_model.set_api_key(Config.AI_API_KEY)
        db.session.add(new_model)
        db.session.commit()
        print("Default model config created.")
    else:
        print(f"Model config already exists: {model.name}")
