from huggingface_hub import HfApi
import os

# Initialize API (uses your saved token)
api = HfApi()

print("📤 Uploading README.md to Hugging Face...")

try:
    # Upload README.md directly
    api.upload_file(
        path_or_fileobj="README.md",
        path_in_repo="README.md",
        repo_id="PrashantRGore/drug-causality-bert-v2-model",
        repo_type="model",
        commit_message="Add comprehensive model card: ADE Corpus V2 citation, 97.6% accuracy, Optuna optimization details"
    )
    
    print("\n✅ README.md uploaded successfully!")
    print("🔗 View at: https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model")
    print("\n📊 Your model card now includes:")
    print("  ✅ 97.6% accuracy metrics")
    print("  ✅ ADE Corpus V2 dataset citation")
    print("  ✅ Optuna hyperparameter optimization details")
    print("  ✅ Usage examples and code snippets")
    print("  ✅ Proper tags for discoverability")
    print("  ✅ Ethical considerations and limitations")
    
except Exception as e:
    print(f"\n❌ Error uploading README: {e}")
    print("\nTroubleshooting:")
    print("1. Check your token has WRITE permissions")
    print("2. Verify repo exists: PrashantRGore/drug-causality-bert-v2-model")
    print("3. Try: huggingface-cli login --token <your-token>")
