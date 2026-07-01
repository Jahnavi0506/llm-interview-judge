"""
Ground Truth Evaluation Dataset

A hand-curated set of question/answer pairs with expert-assigned scores.
Used to measure LLM judge ACCURACY (not just consistency).

Scoring guideline used when assigning human_score:
- 9-10: Complete, accurate, well-structured answer covering all key concepts
- 7-8:  Mostly correct, minor gaps or imprecision
- 5-6:  Partially correct, significant gaps
- 3-4:  Basic awareness only, major misconceptions
- 1-2:  Largely incorrect or irrelevant
- 0:    No meaningful answer
"""

GROUND_TRUTH_DATASET = [
    {
        "id": 1,
        "domain": "LLMs",
        "question": "What is self-attention in Transformers?",
        "key_concepts": ["Query", "Key", "Value", "Softmax", "Attention Weights"],
        "candidate_answer": "Self-attention helps the model focus on important words.",
        "human_score": 2.0,
        "human_reasoning": "Correct high-level intuition only. No mention of QKV, dot product, or softmax mechanism."
    },
    {
        "id": 2,
        "domain": "LLMs",
        "question": "What is self-attention in Transformers?",
        "key_concepts": ["Query", "Key", "Value", "Softmax", "Attention Weights"],
        "candidate_answer": "Self-attention computes Query, Key, and Value vectors for each token through learned linear projections. The dot product of Query and Key vectors is scaled and passed through softmax to produce attention weights, which are used to compute a weighted sum of Value vectors as the output.",
        "human_score": 9.5,
        "human_reasoning": "Covers all key concepts accurately with correct technical detail."
    },
    {
        "id": 3,
        "domain": "Machine Learning",
        "question": "What is overfitting and how do you prevent it?",
        "key_concepts": ["Generalization", "Training Data", "Regularization", "Cross-validation"],
        "candidate_answer": "Overfitting is when a model memorizes training data instead of learning patterns. You can prevent it with regularization, dropout, or getting more training data.",
        "human_score": 7.5,
        "human_reasoning": "Correct definition and reasonable prevention methods, but lacks depth on cross-validation or specific regularization techniques like L1/L2."
    },
    {
        "id": 4,
        "domain": "Machine Learning",
        "question": "What is overfitting and how do you prevent it?",
        "key_concepts": ["Generalization", "Training Data", "Regularization", "Cross-validation"],
        "candidate_answer": "Overfitting is bad for the model.",
        "human_score": 0.5,
        "human_reasoning": "No real explanation of the concept or causes. Just states it's bad without any understanding shown."
    },
    {
        "id": 5,
        "domain": "Deep Learning",
        "question": "Explain the vanishing gradient problem.",
        "key_concepts": ["Backpropagation", "Activation Functions", "Gradient", "Deep Networks"],
        "candidate_answer": "In deep networks, gradients can become very small as they're backpropagated through many layers, especially with sigmoid or tanh activations, because their derivatives are small. This makes early layers learn very slowly. ReLU activations and techniques like batch normalization or residual connections help mitigate this.",
        "human_score": 9.0,
        "human_reasoning": "Accurate explanation of cause and correctly names multiple valid solutions."
    },
    {
        "id": 6,
        "domain": "Deep Learning",
        "question": "Explain the vanishing gradient problem.",
        "key_concepts": ["Backpropagation", "Activation Functions", "Gradient", "Deep Networks"],
        "candidate_answer": "It's when the gradients vanish during training.",
        "human_score": 1.5,
        "human_reasoning": "Just restates the term without explaining why it happens or how to solve it."
    },
    {
        "id": 7,
        "domain": "NLP",
        "question": "What is the difference between stemming and lemmatization?",
        "key_concepts": ["Word Reduction", "Dictionary Form", "Morphology", "Context"],
        "candidate_answer": "Stemming chops off word endings using rules without understanding context, often producing non-words like 'studi' for 'studies'. Lemmatization uses vocabulary and morphological analysis to return the proper dictionary form, like 'study', and considers the word's part of speech.",
        "human_score": 9.0,
        "human_reasoning": "Clear, accurate distinction with concrete examples."
    },
    {
        "id": 8,
        "domain": "NLP",
        "question": "What is the difference between stemming and lemmatization?",
        "key_concepts": ["Word Reduction", "Dictionary Form", "Morphology", "Context"],
        "candidate_answer": "They both reduce words to a base form. Stemming is faster.",
        "human_score": 4.0,
        "human_reasoning": "Captures the general purpose but misses the key distinction of accuracy/context awareness — the core difference being tested."
    },
    {
        "id": 9,
        "domain": "DSA",
        "question": "What is the time complexity of binary search and why?",
        "key_concepts": ["Logarithmic Time", "Divide and Conquer", "Sorted Array"],
        "candidate_answer": "Binary search is O(log n) because it eliminates half the search space at each step. Given n elements, the number of times you can halve n before reaching 1 element is log base 2 of n, which determines the number of comparisons needed.",
        "human_score": 9.5,
        "human_reasoning": "Precise explanation of why it's logarithmic, not just stating the complexity."
    },
    {
        "id": 10,
        "domain": "DSA",
        "question": "What is the time complexity of binary search and why?",
        "key_concepts": ["Logarithmic Time", "Divide and Conquer", "Sorted Array"],
        "candidate_answer": "It's O(log n).",
        "human_score": 3.0,
        "human_reasoning": "Correct answer but no explanation of why — doesn't demonstrate understanding, just memorized fact."
    },
    {
        "id": 11,
        "domain": "Machine Learning",
        "question": "Explain the bias-variance tradeoff.",
        "key_concepts": ["Bias", "Variance", "Underfitting", "Overfitting", "Model Complexity"],
        "candidate_answer": "High bias means the model is too simple and underfits, missing patterns in the data. High variance means the model is too complex and overfits, capturing noise. There's a tradeoff because reducing bias often increases variance and vice versa. The goal is to find the sweet spot of model complexity that minimizes total error.",
        "human_score": 9.0,
        "human_reasoning": "Comprehensive explanation covering both sides of the tradeoff with clear cause and effect."
    },
    {
        "id": 12,
        "domain": "Machine Learning",
        "question": "Explain the bias-variance tradeoff.",
        "key_concepts": ["Bias", "Variance", "Underfitting", "Overfitting", "Model Complexity"],
        "candidate_answer": "Bias is when the model is biased and variance is when it varies a lot.",
        "human_score": 1.0,
        "human_reasoning": "Circular definition that doesn't actually explain either concept or the tradeoff relationship."
    },
    {
        "id": 13,
        "domain": "LLMs",
        "question": "What is the purpose of positional encoding in Transformers?",
        "key_concepts": ["Sequence Order", "Self-Attention Limitation", "Sinusoidal Functions"],
        "candidate_answer": "Since self-attention has no inherent notion of word order (it processes all tokens in parallel), positional encoding injects information about token position into the embeddings. The original Transformer paper used sinusoidal functions of different frequencies so the model can learn relative positions.",
        "human_score": 9.0,
        "human_reasoning": "Correctly identifies why it's needed and the specific mechanism used."
    },
    {
        "id": 14,
        "domain": "LLMs",
        "question": "What is the purpose of positional encoding in Transformers?",
        "key_concepts": ["Sequence Order", "Self-Attention Limitation", "Sinusoidal Functions"],
        "candidate_answer": "It tells the model the position of words.",
        "human_score": 3.5,
        "human_reasoning": "States the surface-level purpose but doesn't explain WHY it's needed (attention has no inherent order) or HOW it works."
    },
    {
        "id": 15,
        "domain": "DSA",
        "question": "What is a hash collision and how is it resolved?",
        "key_concepts": ["Hash Function", "Collision", "Chaining", "Open Addressing"],
        "candidate_answer": "A hash collision occurs when two different keys map to the same index in a hash table. It can be resolved using chaining, where each bucket holds a linked list of entries, or open addressing, where the algorithm probes for the next available slot using methods like linear or quadratic probing.",
        "human_score": 9.0,
        "human_reasoning": "Accurate definition with both major resolution strategies correctly explained."
    },
    {
        "id": 16,
        "domain": "DSA",
        "question": "What is a hash collision and how is it resolved?",
        "key_concepts": ["Hash Function", "Collision", "Chaining", "Open Addressing"],
        "candidate_answer": "When two keys give the same hash value.",
        "human_score": 4.0,
        "human_reasoning": "Correct definition of collision but completely misses resolution strategies, which is half the question."
    },
    {
        "id": 17,
        "domain": "Deep Learning",
        "question": "What is batch normalization and why is it used?",
        "key_concepts": ["Internal Covariate Shift", "Normalization", "Training Stability", "Learning Rate"],
        "candidate_answer": "Batch normalization normalizes layer inputs to have zero mean and unit variance within each mini-batch, reducing internal covariate shift. This stabilizes and speeds up training, allows for higher learning rates, and has a slight regularizing effect.",
        "human_score": 8.5,
        "human_reasoning": "Solid technical explanation covering mechanism and benefits, though could mention learnable scale/shift parameters."
    },
    {
        "id": 18,
        "domain": "Deep Learning",
        "question": "What is batch normalization and why is it used?",
        "key_concepts": ["Internal Covariate Shift", "Normalization", "Training Stability", "Learning Rate"],
        "candidate_answer": "It normalizes the data to make training better.",
        "human_score": 3.0,
        "human_reasoning": "Vague and doesn't explain the actual mechanism, what's being normalized, or specific benefits."
    },
    {
        "id": 19,
        "domain": "NLP",
        "question": "What is TF-IDF and what problem does it solve?",
        "key_concepts": ["Term Frequency", "Inverse Document Frequency", "Word Importance", "Stop Words"],
        "candidate_answer": "TF-IDF stands for Term Frequency-Inverse Document Frequency. It measures how important a word is to a document in a collection by combining how often it appears in that document with how rare it is across all documents. This solves the problem of common words like 'the' dominating word frequency counts, since they appear everywhere and get a low IDF score.",
        "human_score": 9.0,
        "human_reasoning": "Accurate, complete explanation including the specific problem it addresses."
    },
    {
        "id": 20,
        "domain": "NLP",
        "question": "What is TF-IDF and what problem does it solve?",
        "key_concepts": ["Term Frequency", "Inverse Document Frequency", "Word Importance", "Stop Words"],
        "candidate_answer": "TF-IDF is used in NLP for text.",
        "human_score": 0.5,
        "human_reasoning": "No actual explanation of what it stands for, how it works, or what problem it solves."
    }
]


def get_dataset_summary() -> dict:
    """Returns summary statistics of the ground truth dataset."""
    domains = {}
    for item in GROUND_TRUTH_DATASET:
        domains[item["domain"]] = domains.get(item["domain"], 0) + 1

    return {
        "total_items": len(GROUND_TRUTH_DATASET),
        "domains": domains,
        "score_range": (
            min(i["human_score"] for i in GROUND_TRUTH_DATASET),
            max(i["human_score"] for i in GROUND_TRUTH_DATASET)
        )
    }