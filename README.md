---
language: en
license: apache-2.0
tags:
  - token-classification
  - named-entity-recognition
  - pii
model-index:
  - name: piisec-ner-bert
    results: []
---
# PIIsec NER BERT
Fine-tuned BERT model for detecting PII entities (NAME, SSN, MRN, ADDRESS) in medical text.

### 🔗 Pretrained Model
Hosted on [Hugging Face](https://huggingface.co/AtlBrandon1/piisec-ner-bert)

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_id = "AtlBrandon1/piisec-ner-bert"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForTokenClassification.from_pretrained(model_id)
