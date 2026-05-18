# Vec2Text: Training an Embedding Inversion Decoder

> A practical guide to training a model that recovers text from dense embeddings.

---

## 1. What is Vec2Text?

Vec2Text (Morris et al., 2023) demonstrates that dense text embeddings are **not one-way functions** — given only an embedding vector, a trained decoder can reconstruct the original text with surprising fidelity. This has implications for:

- **Privacy**: Embeddings stored in vector databases can leak source text
- **Interpretability**: Understanding what information embeddings encode
- **Concept arithmetic**: Generating natural language descriptions of vector directions (e.g., `entity_centroid - global_centroid`)

### Key Paper

> John X. Morris, Volodymyr Kuleshov, Vitaly Shmatikov, Alexander M. Rush.  
> *"Text Embeddings Reveal (Almost) As Much As Text."*  
> EMNLP 2023. [arXiv:2310.06816](https://arxiv.org/abs/2310.06816)

---

## 2. Architecture Overview

Vec2Text uses an **iterative correction** approach built on a sequence-to-sequence (encoder-decoder) backbone:

```
Embedding Vector (e.g. 4096-dim)
       │
       ▼
┌──────────────┐
│  Projector    │  Linear layer: embed_dim → decoder_hidden_dim
│  (Linear)     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Base Decoder │  T5/GPT-2 decoder: generates initial hypothesis ĥ₀
│  (Seq2Seq)    │
└──────┬───────┘
       │
       ▼  Iterative Correction (steps 1..K)
┌──────────────────────────────────┐
│  Re-embed ĥₖ to get ê           │
│  Corrector input: [e; ê; ĥₖ]    │──┐
│  Generate ĥₖ₊₁                   │  │ repeat K times
└──────────────────────────────────┘◄─┘
       │
       ▼
   Final text ĥ_K
```

### Two-Stage Training

1. **Base Decoder** — learns `embedding → text` mapping from scratch
2. **Corrector** — takes `(target_embedding, hypothesis_embedding, hypothesis_text)` and outputs improved text

The corrector iterates at inference time (typically 20-50 steps), each time re-embedding its output and feeding the residual back in.

---

## 3. Training Data Requirements

### What you need

| Component | Description | Example |
|-----------|-------------|---------|
| **Text corpus** | Large collection of text passages | Wikipedia, C4, your domain-specific data |
| **Embedding model** | The model whose embeddings you want to invert | `qwen3-embedding:8b`, `text-embedding-ada-002`, GTR-base |
| **Pre-computed embeddings** | Embeddings of all training texts | Run batch embedding offline |

### Scale Guidelines

| Dataset Size | Expected Quality | Training Time (1× A100) |
|-------------|------------------|------------------------|
| 100K pairs | Proof of concept, poor generalization | ~2 hours |
| 1M pairs | Decent reconstruction on in-domain data | ~12 hours |
| 10M+ pairs | Good generalization, near-paper quality | ~3-5 days |

### Data Format

Each training example is a `(embedding, text)` pair:

```jsonl
{"embedding": [0.0123, -0.0456, ...], "text": "The quick brown fox jumps over the lazy dog."}
{"embedding": [0.0789, 0.0234, ...], "text": "Machine learning models require large datasets."}
```

### Practical Tips for Data Preparation

- **Chunk text** into passages of similar length (32-128 tokens works well)
- **Deduplicate** to avoid memorization shortcuts
- **Shuffle** thoroughly — no ordering by source
- **Match the embedding model** exactly — Vec2Text is model-specific; a decoder trained on OpenAI embeddings won't work for Ollama embeddings

---

## 4. Training Procedure

### 4.1 Environment Setup

```bash
# Clone the Vec2Text repository
git clone https://github.com/jxmorris12/vec2text.git
cd vec2text

# Install dependencies
pip install -e .
pip install transformers datasets accelerate wandb
```

### 4.2 Stage 1: Base Decoder Training

The base decoder learns to generate an initial text hypothesis from a single embedding vector.

**Architecture choices:**

| Backbone | Parameters | Notes |
|----------|-----------|-------|
| T5-base | 220M | Good balance; used in the paper |
| T5-large | 770M | Better quality, slower |
| GPT-2 | 124M | Decoder-only alternative |

**Key hyperparameters:**

```python
{
    "model": "t5-base",              # Backbone
    "embed_dim": 4096,               # Must match your embedding model
    "max_seq_length": 128,           # Max tokens to reconstruct
    "learning_rate": 2e-4,           # AdamW
    "batch_size": 256,               # Per-GPU
    "warmup_steps": 1000,
    "num_epochs": 50,                # Or until convergence
    "weight_decay": 0.01,
}
```

**Training loop (simplified):**

```python
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

class Vec2TextDecoder(torch.nn.Module):
    def __init__(self, embed_dim, model_name="t5-base"):
        super().__init__()
        self.decoder = T5ForConditionalGeneration.from_pretrained(model_name)
        hidden = self.decoder.config.d_model
        self.projector = torch.nn.Linear(embed_dim, hidden)

    def forward(self, embeddings, labels):
        # Project embedding to decoder hidden dim
        projected = self.projector(embeddings).unsqueeze(1)  # (B, 1, H)
        # Use as encoder output
        outputs = self.decoder(
            encoder_outputs=(projected,),
            labels=labels,
        )
        return outputs.loss

# Training step
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
for batch in dataloader:
    loss = model(batch["embeddings"], batch["token_ids"])
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

**Loss function:** Standard cross-entropy on next-token prediction, same as any seq2seq model.

### 4.3 Stage 2: Corrector Training

The corrector refines the base decoder's output iteratively.

**Training data generation:**

1. Run the base decoder on all training embeddings to produce hypothesis texts ĥ₀
2. Embed the hypotheses to get ê₀
3. Each corrector training example: `(e_target, ê_hypothesis, ĥ_hypothesis) → original_text`

```python
class CorrectorModel(torch.nn.Module):
    def __init__(self, embed_dim, model_name="t5-base"):
        super().__init__()
        self.decoder = T5ForConditionalGeneration.from_pretrained(model_name)
        hidden = self.decoder.config.d_model
        # Takes concatenated [target_emb; hypothesis_emb]
        self.projector = torch.nn.Linear(embed_dim * 2, hidden)

    def forward(self, target_emb, hypothesis_emb, hypothesis_tokens, labels):
        combined = torch.cat([target_emb, hypothesis_emb], dim=-1)
        projected = self.projector(combined).unsqueeze(1)
        # Prepend hypothesis text tokens as additional context
        outputs = self.decoder(
            encoder_outputs=(projected,),
            decoder_input_ids=hypothesis_tokens,
            labels=labels,
        )
        return outputs.loss
```

**Corrector hyperparameters:**

```python
{
    "learning_rate": 1e-4,           # Lower than base decoder
    "batch_size": 128,
    "num_epochs": 20,
    "correction_steps_train": 1,     # Train on single-step corrections
    "correction_steps_inference": 20, # Iterate more at inference
}
```

### 4.4 Multi-Step Inference

At inference, the corrector runs iteratively:

```python
def invert_embedding(target_embedding, base_decoder, corrector, embedder, steps=20):
    # Step 0: base decoder hypothesis
    hypothesis = base_decoder.generate(target_embedding)

    for step in range(steps):
        # Re-embed current hypothesis
        hyp_embedding = embedder.encode(hypothesis)
        # Corrector produces improved text
        hypothesis = corrector.generate(target_embedding, hyp_embedding, hypothesis)
        # Optional: check convergence
        sim = cosine_similarity(embedder.encode(hypothesis), target_embedding)
        if sim > 0.999:
            break

    return hypothesis
```

---

## 5. Loss Functions

### Primary: Cross-Entropy (CE)

Standard teacher-forced cross-entropy — the workhorse of seq2seq training.

### Optional: Embedding Cosine Loss

Add a term that penalizes when the re-embedded output is far from the target:

```python
def combined_loss(ce_loss, output_text, target_embedding, embedder, alpha=0.1):
    output_embedding = embedder.encode(output_text)
    cosine_loss = 1 - F.cosine_similarity(output_embedding, target_embedding)
    return ce_loss + alpha * cosine_loss.mean()
```

### Optional: BLEU/ROUGE Reward (RL fine-tuning)

After supervised training, fine-tune with REINFORCE using BLEU as reward:

```python
reward = compute_bleu(generated_text, reference_text)
loss = -log_prob * (reward - baseline)
```

---

## 6. Evaluation Metrics

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **BLEU** | N-gram overlap between original and reconstructed text | >0.90 (32-token passages) |
| **Exact Match** | Fraction of perfectly reconstructed passages | >0.30 (ambitious) |
| **Cosine Similarity** | Embedding similarity between original and reconstruction | >0.99 |
| **Token F1** | Token-level precision/recall | >0.95 |

---

## 7. Adapting for ThoughtMap

Vec2Text should be treated as one part of the broader ThoughtMap model-optimization layer, not as the first model to train. The most immediate quality win is likely a fine-tuned Entity Type Resolver, because current NER mistakes are concrete and easy to evaluate. See [[model-optimization-finetuning-plan|Model Optimization and Fine-Tuning Plan]] for the recommended order.

### Use Case: Concept Arithmetic Narration

Instead of inverting a single embedding, describe the *direction* between two embeddings:

```
direction_vector = entity_centroid - global_centroid
→ "What text would live in this direction?"
→ Train Vec2Text to narrate it
```

### Domain-Specific Training Data

For a personal knowledge base like ThoughtMap:

1. **Extract all chunks** from ChromaDB (~8K chunks)
2. **Get their embeddings** from the qwen3-embedding:8b model
3. **Train a small decoder** (T5-base) on these (embedding, text) pairs
4. The model learns the specific "language" of your knowledge base

### Practical Shortcut: Nearest-Neighbor + LLM

If training a full Vec2Text model is too heavy, a simpler alternative (what ThoughtMap currently does):

1. Compute the difference vector via concept arithmetic
2. Find K nearest chunks to that vector (cosine similarity)
3. Send those chunks to an LLM with a prompt explaining the task
4. The LLM generates a natural language description

This avoids training entirely but requires an LLM at inference time.

---

## 8. Hardware Requirements

| Stage | Min GPU | Recommended | VRAM |
|-------|---------|-------------|------|
| Data embedding | CPU or GPU | 1× GPU | 8GB+ |
| Base decoder (T5-base) | 1× A100 | 1× A100 | 40GB |
| Base decoder (T5-base, smaller batch) | 1× RTX 3090 | 1× RTX 4090 | 24GB |
| Corrector training | 1× A100 | 2× A100 | 40GB+ |
| Inference only | CPU or 1× GPU | 1× RTX 3090 | 16GB |

### Saving VRAM

- Use `bfloat16` or `float16` mixed precision
- Gradient checkpointing for T5-large
- Reduce batch size + use gradient accumulation

---

## 9. Full Training Recipe (Step by Step)

```bash
# 1. Prepare data
python prepare_data.py \
  --input chunks.json \
  --embedding-model qwen3-embedding:8b \
  --output train_pairs.jsonl

# 2. Train base decoder
python train_base.py \
  --data train_pairs.jsonl \
  --embed-dim 4096 \
  --backbone t5-base \
  --epochs 50 \
  --batch-size 256 \
  --lr 2e-4 \
  --output checkpoints/base/

# 3. Generate hypotheses for corrector training
python generate_hypotheses.py \
  --model checkpoints/base/best.pt \
  --data train_pairs.jsonl \
  --output hypotheses.jsonl

# 4. Train corrector
python train_corrector.py \
  --data train_pairs.jsonl \
  --hypotheses hypotheses.jsonl \
  --embed-dim 4096 \
  --backbone t5-base \
  --epochs 20 \
  --batch-size 128 \
  --lr 1e-4 \
  --output checkpoints/corrector/

# 5. Evaluate
python evaluate.py \
  --base checkpoints/base/best.pt \
  --corrector checkpoints/corrector/best.pt \
  --test test_pairs.jsonl \
  --correction-steps 20
```

---

## 10. References

1. Morris, J.X., Kuleshov, V., Shmatikov, V., Rush, A.M. (2023). *Text Embeddings Reveal (Almost) As Much As Text.* EMNLP 2023. [arXiv:2310.06816](https://arxiv.org/abs/2310.06816)
2. Li, Y., et al. (2023). *Sentence Embeddings Leakage through Embedding Inversion.* [arXiv:2305.03010](https://arxiv.org/abs/2305.03010)
3. Morris, J.X. GitHub repository: [jxmorris12/vec2text](https://github.com/jxmorris12/vec2text)
4. Raffel, C., et al. (2020). *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer.* JMLR. (T5 backbone)

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Embedding inversion** | Recovering original text from its dense vector representation |
| **Concept arithmetic** | Vector operations on embeddings (e.g., king - man + woman = queen) |
| **Iterative correction** | Multi-step refinement where each step re-embeds and corrects |
| **Projector** | Linear layer mapping embedding dimension to decoder hidden dimension |
| **Hypothesis** | The decoder's current best guess for the original text |
| **Cosine similarity** | Similarity metric between vectors; 1.0 = identical direction |
