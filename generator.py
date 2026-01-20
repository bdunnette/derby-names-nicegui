import markovify
import httpx
from pathlib import Path
import random
import json


class DerbyNameGenerator:
    """Generate roller derby names using word and character-level Markov chains."""

    DERBY_NAMES_URL = "https://raw.githubusercontent.com/bdunnette/derby-name-scraper/main/data/derby_names.txt"
    CACHE_FILE = Path(__file__).parent / "data" / "derby_names.txt"
    WORD_MODEL_FILE = Path(__file__).parent / "data" / "markov_word_model.json"
    CHAR_MODEL_FILE = Path(__file__).parent / "data" / "markov_char_model.json"
    WORD_MODEL_WEIGHT = 0.7
    CHAR_MODEL_WEIGHT = 0.3
    MODEL_STATE_SIZE = 2

    def __init__(self):
        self.word_model = None
        self.char_model = None
        self.names_text = None
        self._load_or_download_names()
        self._load_or_train_models()

    def _load_or_download_names(self):
        """Load derby names from cache or download from GitHub."""
        # Create data directory if it doesn't exist
        self.CACHE_FILE.parent.mkdir(exist_ok=True)

        # Download if cache doesn't exist
        if not self.CACHE_FILE.exists():
            print("Downloading derby names from GitHub...")
            response = httpx.get(self.DERBY_NAMES_URL)
            response.raise_for_status()
            self.CACHE_FILE.write_text(response.text, encoding="utf-8")
            print(f"Downloaded {len(response.text.splitlines())} derby names")

        # Load the names
        self.names_text = self.CACHE_FILE.read_text(encoding="utf-8")

    def _load_or_train_models(self):
        """Load pre-trained models from disk or train new ones."""
        models_exist = self.WORD_MODEL_FILE.exists() and self.CHAR_MODEL_FILE.exists()

        # Try to load existing models
        if models_exist:
            try:
                print("Loading pre-trained Markov models...")

                # Load word-level model
                with open(self.WORD_MODEL_FILE, "r", encoding="utf-8") as f:
                    word_model_json = json.load(f)
                self.word_model = markovify.NewlineText.from_json(word_model_json)

                # Load character-level model
                with open(self.CHAR_MODEL_FILE, "r", encoding="utf-8") as f:
                    char_model_json = json.load(f)
                self.char_model = markovify.Text.from_json(char_model_json)

                print("Markov models loaded successfully")
                return
            except Exception as e:
                print(f"Error loading models, will retrain: {e}")

        # Train new models if loading failed or files don't exist
        self._train_models()

        # Save the trained models
        try:
            print("Saving trained models...")

            # Save word-level model
            word_model_json = self.word_model.to_json()
            with open(self.WORD_MODEL_FILE, "w", encoding="utf-8") as f:
                json.dump(word_model_json, f)

            # Save character-level model
            char_model_json = self.char_model.to_json()
            with open(self.CHAR_MODEL_FILE, "w", encoding="utf-8") as f:
                json.dump(char_model_json, f)

            print("Models saved successfully")
        except Exception as e:
            print(f"Warning: Could not save models: {e}")

    def _train_models(self):
        """Train both word-level and character-level Markov models."""
        print("Training Markov models...")

        # Train word-level model (state_size=2 for better coherence)
        print("  - Training word-level model...")
        self.word_model = markovify.NewlineText(
            self.names_text, state_size=self.MODEL_STATE_SIZE
        )

        # Train character-level model (state_size=2 to match word model)
        print("  - Training character-level model...")
        self.char_model = markovify.Text(
            self.names_text, state_size=self.MODEL_STATE_SIZE
        )

        print("Markov models trained successfully")

    def generate(self, max_attempts: int = 100) -> str:
        """
        Generate a new derby name by randomly choosing between word and character models.

        Args:
            max_attempts: Maximum number of generation attempts

        Returns:
            A generated derby name
        """
        if not self.word_model or not self.char_model:
            raise RuntimeError("Models not trained")

        # Randomly choose between word-level (70%) and character-level (30%) models
        # This avoids the Markovify limitation of combining different model types
        for _ in range(max_attempts):
            if random.random() < self.WORD_MODEL_WEIGHT:
                # Use word-level model for coherence
                name = self.word_model.make_sentence(tries=100)
            else:
                # Use character-level model for creativity
                name = self.char_model.make_sentence(tries=100)

            if name:
                return name

        # Final fallback: return a random name from the training data
        names = [n.strip() for n in self.names_text.split("\n") if n.strip()]
        return random.choice(names)


# Global generator instance
_generator = None


def get_generator() -> DerbyNameGenerator:
    """Get or create the global name generator instance."""
    global _generator
    if _generator is None:
        _generator = DerbyNameGenerator()
    return _generator
