from huggingface_hub import HfApi
import os

# Initialize API (uses your saved token)
api = HfApi()

print("📤 Uploading Model Card to Hugging Face...")

try:
    # Upload MODEL_CARD.md directly as README.md in the Hugging Face repository
    api.upload_file(
        path_or_fileobj="MODEL_CARD.md",
        path_in_repo="README.md",
        repo_id="PrashantRGore/drug-causality-bert-v2-model",
        repo_type="model",
        commit_message="Add comprehensive model card: ADE Corpus V2 citation, 97.6% accuracy, Optuna optimization details"
    )
    
    print("\n✅ Model Card uploaded successfully to Hugging Face!")
    print("🔗 View at: https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model")
    
except Exception as e:
    print(f"\n❌ Error uploading model card: {e}")
    print("\nTroubleshooting:")
    print("1. Check your token has WRITE permissions")
    print("2. Verify repo exists: PrashantRGore/drug-causality-bert-v2-model")
    print("3. Try: huggingface-cli login --token <your-token>")
