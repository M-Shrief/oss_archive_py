# Notes

## AI
### AI repos structure
Don't feel weird when dealing with AI repos and their project structure, they're not like web development or other fields.

For example, DeepSeek V3 structure is:
- figures/
- inference/
- .gitattributes
- LICENSE-CODE
- LICENSE-MODEL
- README.md
- README_WEIGHTS.md
- config.json
- configuration_deepseek.py
- model-00001-of-000163.safetensors
- ...
- model-00163-of-000163.safetensors
- model.safetensors.index.json
- modeling_deepseek.py
- tokenizer.json
- tokenizer_config.json

As This layout follows standard practices:
- **Model Weights**: The `.safetensors` files (e.g., `model-00001-of-000163.safetensors`) contain the trained model parameters, split into shards for efficient loading.
- **Configuration**: `config.json`, `configuration_deepseek.py`, and `modeling_deepseek.py` define the model architecture, hyperparameters, and class definitions needed to load and run the model.
- **Tokenizer Files**: `tokenizer.json`, `tokenizer_config.json` handle text encoding/decoding, crucial for input/output processing.
- **Documentation**: `README.md`, `LICENSE-CODE`, `LICENSE-MODEL`, and `README_WEIGHTS.md` provide usage instructions, licensing, and model details — essential for open-source compliance and usability.
- **Metadata**: `.gitattributes` manages Git behavior for large files, especially with Git LFS.

This structure ensures the model is **reproducible, distributable, and usable** across different environments, aligning with both Hugging Face standards and broader open-model practices.



