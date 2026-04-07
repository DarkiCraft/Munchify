from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models" / "saved"

# Create dirs if not exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Data generation config
NUM_USERS = 100
NUM_ITEMS = 50
NUM_INTERACTIONS = 2000

# Model Config
EMBEDDING_DIM = 32
LEARNING_RATE = 0.001
EPOCHS = 10
BATCH_SIZE = 32
