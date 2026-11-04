# Legal-act-classification
Classify laws and regulations by legal area (tax, labour, education, health...) trained on Croatian legal acts that work on Bosnian and Serbian

# Team:
- Nejra Zurapi
- Faris Sačić
- Nađa Milanović

## Project Overview

This project focuses on cross-lingual legal act classification. The goal is to train a text classification model using Croatian legal acts and evaluate its performance on Bosnian and Serbian legal documents.

## Project Objectives

- Prepare and analyze the Croatian MultiEURLEX dataset.
- Create a shared taxonomy of ten legal areas.
- Train baseline machine learning models.
- Fine-tune the BERTić language model.
- Evaluate model performance on Bosnian and Serbian legal acts.
- Compare classification performance across languages.

## Legal Areas

The project uses the following ten legal categories:

1. Constitutional Law
2. Criminal Law
3. Civil Law
4. Public Administration
5. Taxation and Finance
6. Employment and Social Protection
7. Healthcare
8. Education and Culture
9. Economy and Business
10. Environment and Infrastructure

Detailed classification rules are available in [Annotation Guidelines](docs/annotation_guidelines.md).

## Dataset

### Training Data
- Source: MultiEURLEX
- Language: Croatian
- Configuration: `hr`
- Label level: EUROVOC Level 2
- Splits: Training, validation, and test

### Evaluation Data

- Bosnian legal acts from the Official Gazette of Bosnia and Herzegovina.
- Serbian legal acts from the Legal Information System of the Republic of Srpska.

The goal is to evaluate cross-lingual transfer without training the models on Bosnian or Serbian documents.

## Research Questions

- **RQ1:** How accurately can legal acts be classified in Croatian?
- **RQ2:** How well does a model trained on Croatian legal acts transfer to Bosnian and Serbian?
- **RQ3:** How large is the performance drop when transferring from Croatian to Bosnian and Serbian?

## Methodology

The planned classification pipeline consists of:

1. Dataset collection and preparation.
2. EUROVOC label mapping to the shared legal taxonomy.
3. Text preprocessing and analysis.
4. Baseline model training using TF-IDF with Logistic Regression or Linear SVM.
5. Fine-tuning the BERTić language model.
6. Evaluation on Croatian, Bosnian, and Serbian datasets.
7. Cross-lingual performance comparison.

## Evaluation Metrics

The models will be evaluated using:

- Macro-F1
- Micro-F1
- Per-class F1-score
- Cross-lingual F1-score drop

## Project Structure

```text
Legal-act-classification/
├── docs/
│   └── annotation_guidelines.md
├── src/
│   ├── labels.py
│   ├── eurovoc_mapping.py
│   ├── inspect_level2.py
│   └── prepare_multieurlex.py
├── .gitignore
├── requirements.txt
└── README.md
```