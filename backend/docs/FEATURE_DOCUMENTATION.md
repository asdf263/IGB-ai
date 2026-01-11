# Feature Extraction Documentation

This document describes all features extracted from chat conversations, their types (raw vs synthetic/composite), calculation methods, and what the LLM personality system uses.

---

## Feature Categories Overview

| Category | Module | Feature Count | Type |
|----------|--------|---------------|------|
| Temporal | `temporal_features.py` | ~15 | Raw |
| Text | `text_features.py` | 25 | Raw |
| Linguistic | `linguistic_features_spacy.py` | 30 | Raw |
| Semantic | `semantic_features_hf.py` | ~20 | Raw |
| Sentiment | `sentiment_features.py` | 20 | Raw |
| Behavioral | `behavioral_features.py` | 25 | Raw |
| Graph | `graph_features.py` | ~15 | Raw |
| Reaction | `reaction_features.py` | 30 | Raw |
| Composite | `composite_features.py` | 15 | Synthetic |
| **Emotion** | `emotion_transformer.py` | **20** | **Raw (Transformer)** |
| **Context** | `conversation_context_features.py` | **25** | **Raw** |
| LLM Synthetic | `llm_synthetic_features.py` | 20 | Synthetic |

**Total: ~265 features**

---

## Raw Features

### 1. Text Features (`text_features.py`)

Basic text structure and metrics extracted directly from message content.

| Feature | Description | Range |
|---------|-------------|-------|
| `msg_length_mean` | Average message length in characters | 0-∞ |
| `msg_length_std` | Standard deviation of message lengths | 0-∞ |
| `msg_length_min` | Minimum message length | 0-∞ |
| `msg_length_max` | Maximum message length | 0-∞ |
| `msg_length_median` | Median message length | 0-∞ |
| `word_count_mean` | Average words per message | 0-∞ |
| `word_count_std` | Standard deviation of word counts | 0-∞ |
| `char_per_word_mean` | Average characters per word | 0-∞ |
| `sentence_count_mean` | Average sentences per message | 0-∞ |
| `words_per_sentence_mean` | Average words per sentence | 0-∞ |
| `lexical_richness` | Unique words / total words | 0-1 |
| `type_token_ratio` | Same as lexical_richness | 0-1 |
| `hapax_legomena_ratio` | Words appearing once / unique words | 0-1 |
| `shannon_entropy` | Word distribution entropy | 0-∞ |
| `char_entropy` | Character distribution entropy | 0-∞ |
| `stopword_ratio` | Stopwords / total words | 0-1 |
| `uppercase_ratio` | Uppercase chars / total chars | 0-1 |
| `digit_ratio` | Digit chars / total chars | 0-1 |
| `punctuation_ratio` | Punctuation / total chars | 0-1 |
| `whitespace_ratio` | Whitespace / total chars | 0-1 |
| `emoji_density` | Emojis / total words | 0-∞ |
| `url_density` | URLs / total words | 0-∞ |
| `mention_density` | @mentions / total words | 0-∞ |
| `hashtag_density` | #hashtags / total words | 0-∞ |
| `question_mark_ratio` | Question marks / message count | 0-∞ |

### 2. Linguistic Features (`linguistic_features_spacy.py`)

Grammar and syntax features extracted using spaCy NLP.

| Feature | Description | Range |
|---------|-------------|-------|
| `pos_noun_ratio` | Nouns / total tokens | 0-1 |
| `pos_verb_ratio` | Verbs / total tokens | 0-1 |
| `pos_adj_ratio` | Adjectives / total tokens | 0-1 |
| `pos_adv_ratio` | Adverbs / total tokens | 0-1 |
| `pos_pronoun_ratio` | Pronouns / total tokens | 0-1 |
| `pos_preposition_ratio` | Prepositions / total tokens | 0-1 |
| `pos_conjunction_ratio` | Conjunctions / total tokens | 0-1 |
| `pos_interjection_ratio` | Interjections / total tokens | 0-1 |
| `pos_determiner_ratio` | Determiners / total tokens | 0-1 |
| `pos_auxiliary_ratio` | Auxiliary verbs / total tokens | 0-1 |
| `first_person_ratio` | First-person pronouns / all pronouns | 0-1 |
| `second_person_ratio` | Second-person pronouns / all pronouns | 0-1 |
| `third_person_ratio` | Third-person pronouns / all pronouns | 0-1 |
| `past_tense_ratio` | Past tense verbs / all verbs | 0-1 |
| `present_tense_ratio` | Present tense verbs / all verbs | 0-1 |
| `future_tense_ratio` | Future tense verbs / all verbs | 0-1 |
| `modal_verb_ratio` | Modal verbs / all verbs | 0-1 |
| `named_entity_count` | Total named entities found | 0-∞ |
| `entity_person_ratio` | PERSON entities / all entities | 0-1 |
| `entity_org_ratio` | ORG entities / all entities | 0-1 |
| `entity_location_ratio` | Location entities / all entities | 0-1 |
| `avg_dependency_depth` | Average syntax tree depth | 0-∞ |
| `avg_noun_chunks` | Noun chunks per sentence | 0-∞ |
| `subordinate_clause_ratio` | Subordinate markers / sentences | 0-∞ |
| `passive_voice_ratio` | Passive constructions / sentences | 0-∞ |
| `negation_ratio` | Negations / total tokens | 0-1 |
| `question_ratio` | Questions / sentences | 0-∞ |
| `exclamation_ratio` | Exclamations / sentences | 0-∞ |
| `avg_sentence_length` | Average tokens per sentence | 0-∞ |
| `readability_score` | Flesch-Kincaid readability | 0-100 |

### 3. Sentiment Features (`sentiment_features.py`)

Emotional and sentiment analysis features.

| Feature | Description | Range | Notes |
|---------|-------------|-------|-------|
| `sentiment_mean` | Average sentiment score | -1 to 1 | |
| `sentiment_std` | Sentiment standard deviation | 0-1 | |
| `sentiment_min` | Minimum sentiment | -1 to 1 | |
| `sentiment_max` | Maximum sentiment | -1 to 1 | |
| `sentiment_range` | Max - Min sentiment | 0-2 | |
| `sentiment_skewness` | Sentiment distribution skew | -∞ to ∞ | |
| `positive_ratio` | Positive messages / total | 0-1 | |
| `negative_ratio` | Negative messages / total | 0-1 | |
| `neutral_ratio` | Neutral messages / total | 0-1 | |
| `sentiment_volatility` | Average absolute sentiment change | 0-2 | |
| `sentiment_trend` | Linear trend slope | -∞ to ∞ | |
| `sentiment_consistency` | 1 / (1 + std) | 0-1 | |
| `emotion_joy_ratio` | Joy words / total emotion words | 0-1 | **Often 0** |
| `emotion_sadness_ratio` | Sadness words / total emotion words | 0-1 | **Often 0** |
| `emotion_anger_ratio` | Anger words / total emotion words | 0-1 | **Often 0** |
| `emotion_fear_ratio` | Fear words / total emotion words | 0-1 | **Often 0** |
| `emotion_surprise_ratio` | Surprise words / total emotion words | 0-1 | **Often 0** |
| `emotion_disgust_ratio` | Disgust words / total emotion words | 0-1 | **Often 0** |
| `emotional_intensity_mean` | Average intensity (intensifiers + punctuation) | 0-1 | |
| `emotional_shift_frequency` | Significant sentiment shifts / transitions | 0-1 | |

**Known Issue**: Emotion ratios often zero out because they rely on exact word matches from small lexicons. Most casual conversation doesn't use explicit emotion words like "joyful" or "furious".

### 4. Behavioral Features (`behavioral_features.py`)

Conversational behavior and social signal patterns.

| Feature | Description | Range |
|---------|-------------|-------|
| `response_rate` | Responses to bot / opportunities | 0-1 |
| `initiation_rate` | Initiations / user messages | 0-1 |
| `avg_turn_length` | Average messages per turn | 0-∞ |
| `turn_length_variance` | Variance in turn lengths | 0-∞ |
| `question_frequency` | Questions / total messages | 0-1 |
| `answer_frequency` | Answer-starting messages / total | 0-1 |
| `affirmation_frequency` | Affirmations / total messages | 0-∞ |
| `elaboration_score` | Average word count / 50 (capped at 1) | 0-1 |
| `politeness_score` | Politeness markers / words × 10 | 0-1 |
| `formality_score` | (formal - informal markers) normalized | 0-1 |
| `humor_density` | Humor markers / words | 0-∞ |
| `sarcasm_probability` | Sarcasm indicators normalized | 0-1 |
| `empathy_score` | Empathy phrases / messages | 0-1 |
| `directness_score` | 1 - (hedges / words × 10) | 0-1 |
| `assertiveness_score` | Assertive markers / words × 10 | 0-1 |
| `engagement_level` | User messages / total × 2 | 0-1 |
| `reciprocity_index` | 1 - |user - bot| / total | 0-1 |
| `dominance_score` | User words / total words | 0-1 |
| `topic_control_ratio` | Questions / user messages | 0-1 |
| `interruption_proxy` | Short responses / user messages | 0-1 |
| `agreement_ratio` | Agreement words / total words | 0-∞ |
| `disagreement_ratio` | Disagreement words / total words | 0-∞ |
| `support_ratio` | Support phrases / messages | 0-1 |
| `criticism_ratio` | Criticism phrases / messages | 0-1 |
| `self_disclosure_level` | Self-disclosure phrases / messages | 0-1 |

### 5. Reaction Features (`reaction_features.py`)

How a user reacts to the other person's messages.

| Feature | Description | Range |
|---------|-------------|-------|
| `response_enthusiasm` | Exclamations + positive words + length | 0-1 |
| `response_length_ratio` | Response length / trigger length | 0-1 |
| `response_speed_consistency` | (Placeholder - needs timestamps) | 0.5 |
| `engagement_after_questions` | Response quality after questions | 0-1 |
| `engagement_after_statements` | Response quality after statements | 0-1 |
| `sentiment_mirroring` | Same sentiment direction rate | 0-1 |
| `sentiment_amplification` | Stronger same-direction sentiment | 0-1 |
| `sentiment_dampening` | Weaker same-direction sentiment | 0-1 |
| `emotional_responsiveness` | Response to emotional triggers | 0-1 |
| `mood_influence_susceptibility` | Correlation of trigger/response sentiment | 0-1 |
| `topic_following_rate` | Shared words / trigger words | 0-1 |
| `topic_expansion_rate` | New words added / 10 | 0-1 |
| `topic_deflection_rate` | Complete topic changes | 0-1 |
| `semantic_alignment` | Word overlap average | 0-1 |
| `conversation_steering` | Questions in responses | 0-1 |
| `affirmation_tendency` | Affirmation words in responses | 0-1 |
| `disagreement_tendency` | Disagreement words in responses | 0-1 |
| `elaboration_on_partner_topics` | Response length / 30 | 0-1 |
| `question_responsiveness` | Response quality to questions | 0-1 |
| `support_reactivity` | Support words in responses | 0-1 |
| `attention_consistency` | 1 / (1 + response length variance) | 0-1 |
| `interest_signal_rate` | Interest words / 3 | 0-1 |
| `disengagement_signals` | Disengagement words / 3 | 0-1 |
| `reciprocity_balance` | min/max message counts | 0-1 |
| `conversation_investment` | Total words / 500 | 0-1 |
| `style_adaptation` | Average of matching scores | 0-1 |
| `formality_matching` | Formality level matching | 0-1 |
| `energy_matching` | Length + punctuation matching | 0-1 |
| `vocabulary_convergence` | Shared vocabulary rate | 0-1 |
| `communication_synchrony` | Same as style_adaptation | 0-1 |

---

## Synthetic/Composite Features

### 6. Composite Features (`composite_features.py`)

Derived features combining multiple raw features.

| Feature | Calculation | Range |
|---------|-------------|-------|
| `social_energy_index` | msg_length × frequency × sentiment | 0-1 |
| `emotional_volatility_index` | sentiment_std × latency_variance | 0-1 |
| `attentiveness_index` | (question_freq + response_rate + speed) / 3 | 0-1 |
| `confidence_index` | (assertive / hedge + assertiveness) / 2 | 0-1 |
| `expressiveness_index` | (emoji × 10 + sentiment_range + intensity) / 3 | 0-1 |
| `topic_coherence_score` | (coherence + concentration) / 2 | 0-1 |
| `communication_efficiency` | (richness + elaboration) × length_factor | 0-1 |
| `engagement_quality` | (engagement + response_rate + positive) / 3 | 0-1 |
| `personality_consistency` | 1 - |formality - directness| | 0-1 |
| `interaction_rhythm_score` | (1 - burstiness + balance) / 2 | 0-1 |
| `semantic_richness` | (entropy + diversity) / 2 | 0-1 |
| `conversational_depth` | (clause_depth + elaboration + abstraction) / 3 | 0-1 |
| `responsiveness_quality` | (speed_score + response_rate) / 2 | 0-1 |
| `emotional_intelligence_proxy` | (empathy + support + consistency) / 3 | 0-1 |
| `overall_behavior_score` | Mean of all composite features | 0-1 |

### 7. Emotion Transformer Features (`emotion_transformer.py`)

**NEW**: Transformer-based emotion detection using HuggingFace models (replaces word-list based detection).

Uses model: `SamLowe/roberta-base-go_emotions` (27 emotion labels, mapped to 10 categories)

| Feature | Description | Range |
|---------|-------------|-------|
| `emotion_joy_score` | Joy/happiness intensity | 0-1 |
| `emotion_sadness_score` | Sadness intensity | 0-1 |
| `emotion_anger_score` | Anger intensity | 0-1 |
| `emotion_fear_score` | Fear/anxiety intensity | 0-1 |
| `emotion_surprise_score` | Surprise intensity | 0-1 |
| `emotion_disgust_score` | Disgust intensity | 0-1 |
| `emotion_love_score` | Love/affection intensity | 0-1 |
| `emotion_optimism_score` | Optimism intensity | 0-1 |
| `emotion_trust_score` | Trust intensity | 0-1 |
| `emotion_anticipation_score` | Anticipation/excitement intensity | 0-1 |
| `dominant_emotion_consistency` | How consistent is the dominant emotion | 0-1 |
| `emotion_diversity` | How many different emotions expressed | 0-1 |
| `emotion_intensity_mean` | Average emotional intensity | 0-1 |
| `emotion_intensity_max` | Maximum emotional intensity | 0-1 |
| `positive_emotion_ratio` | Positive / total emotions | 0-1 |
| `negative_emotion_ratio` | Negative / total emotions | 0-1 |
| `emotion_transition_rate` | How often dominant emotion changes | 0-1 |
| `emotional_range` | Range of emotional intensity | 0-1 |
| `emotion_entropy` | Entropy of emotion distribution | 0-1 |
| `mixed_emotion_frequency` | How often multiple emotions co-occur | 0-1 |

**Advantages over word-list approach**:
- Detects emotions from context, not just explicit words
- Handles sarcasm, irony, and implicit emotions better
- Works with casual language, slang, and typos
- Provides confidence scores, not binary detection

### 8. Conversation Context Features (`conversation_context_features.py`)

**NEW**: Features about conversation flow, topic transitions, and dialogue dynamics.

| Feature | Description | Range |
|---------|-------------|-------|
| `topic_continuity_score` | How well topics flow between messages | 0-1 |
| `topic_introduction_rate` | How often new topics are introduced | 0-1 |
| `topic_depth_score` | How long topics are sustained | 0-1 |
| `topic_breadth_score` | Diversity of topics discussed | 0-1 |
| `topic_return_frequency` | How often previous topics are revisited | 0-1 |
| `exchange_balance` | Balance of messages between participants | 0-1 |
| `conversation_momentum` | Are messages getting longer/shorter | 0-1 |
| `dialogue_density` | Average message length relative to norm | 0-1 |
| `response_relevance_mean` | How relevant responses are to triggers | 0-1 |
| `tangent_frequency` | How often conversation goes off-topic | 0-1 |
| `turn_taking_regularity` | How regular is the alternation | 0-1 |
| `monologue_tendency` | Tendency for consecutive messages | 0-1 |
| `interruption_pattern` | Short responses after long messages | 0-1 |
| `conversation_dominance_shift` | How much dominance changes over time | 0-1 |
| `speaking_time_variance` | Variance in message lengths by sender | 0-1 |
| `engagement_trajectory` | Is engagement increasing or decreasing | 0-1 |
| `attention_decay_rate` | How quickly engagement drops | 0-1 |
| `re_engagement_frequency` | How often engagement spikes after dip | 0-1 |
| `peak_engagement_timing` | When is engagement highest (0=start, 1=end) | 0-1 |
| `engagement_volatility` | How much engagement fluctuates | 0-1 |
| `opening_warmth` | Warmth in conversation opening | 0-1 |
| `closing_warmth` | Warmth in conversation closing | 0-1 |
| `mid_conversation_depth` | Engagement in middle of conversation | 0-1 |
| `phase_transition_smoothness` | How smooth are phase transitions | 0-1 |
| `conversation_arc_completeness` | Does it have proper opening/closing | 0-1 |

### 9. LLM Synthetic Features (`llm_synthetic_features.py`)

High-level abstracted features designed for LLM personality synthesis. These are more interpretable and robust than raw features.

| Feature | Description | Calculation |
|---------|-------------|-------------|
| `communication_warmth` | Overall warmth/friendliness | sentiment + empathy + support + positive_ratio |
| `intellectual_engagement` | Depth of thought/analysis | vocabulary_richness + question_freq + elaboration + complexity |
| `social_dominance` | Conversational control | initiation + dominance + assertiveness + topic_control |
| `emotional_expressiveness` | Emotional display level | emoji + exclamation + sentiment_range + intensity |
| `conversational_energy` | Overall energy/enthusiasm | response_enthusiasm + engagement + word_count + exclamation |
| `linguistic_sophistication` | Language complexity | readability + lexical_richness + sentence_length + vocabulary |
| `interpersonal_attunement` | Responsiveness to others | mirroring + matching + responsiveness + alignment |
| `self_focus_tendency` | Self vs other orientation | first_person + self_disclosure + topic_deflection |
| `humor_playfulness` | Lightheartedness | humor_density + lol_ratio + playful_markers |
| `formality_level` | Formal vs casual style | formality + formal_markers - informal_markers |
| `agreement_orientation` | Agreeable vs challenging | affirmation + agreement - disagreement |
| `emotional_stability` | Consistency of mood | 1 - volatility - sentiment_std |
| `curiosity_openness` | Interest in new topics | question_freq + topic_expansion + interest_signals |
| `supportiveness` | Tendency to support others | support_ratio + empathy + encouragement |
| `directness_clarity` | Clear vs hedged communication | directness + assertiveness - hedge_ratio |

---

## What the LLM Personality System Uses

The `PersonalityService` builds a **Personality Vector** with 16 dimensions, primarily sourced from **synthetic features** (which are pre-computed abstractions that combine multiple raw features for robustness).

### Personality Vector Dimensions

| Dimension | Primary Source | Fallback Sources | Description |
|-----------|---------------|------------------|-------------|
| `warmth` | `synthetic_communication_warmth` | empathy_score, positive_ratio | Friendliness and warmth |
| `energy` | `synthetic_conversational_energy` | response_enthusiasm, engagement_level | Energy and enthusiasm |
| `formality` | `synthetic_formality_level` | formality_score, politeness_score | Formal vs casual style |
| `directness` | `synthetic_directness_clarity` | directness_score, assertiveness_score | Straightforward vs indirect |
| `emotional_expressiveness` | `synthetic_emotional_expressiveness` | emoji_density, exclamation_ratio | Emotional display level |
| `positivity` | `synthetic_positivity_bias` | positive_ratio, sentiment_mean | Positive vs negative tone |
| `emotional_stability` | `synthetic_emotional_stability` | sentiment_consistency, volatility | Emotional consistency |
| `curiosity` | `synthetic_curiosity_openness` | question_frequency, question_mark_ratio | Interest in exploring topics |
| `supportiveness` | `synthetic_supportiveness` | support_ratio, empathy_score | Tendency to support others |
| `agreement_orientation` | `synthetic_agreement_orientation` | affirmation_tendency, agreement_ratio | Agreeable vs challenging |
| `verbosity` | `synthetic_verbosity_level` | word_count_mean, elaboration_score | Response length/detail |
| `sophistication` | `synthetic_linguistic_sophistication` | lexical_richness, readability_score | Language complexity |
| `humor` | `synthetic_humor_playfulness` | humor_density, emoji_density | Humor and playfulness |
| `self_focus` | `synthetic_self_focus_tendency` | first_person_ratio, self_disclosure_level | Self vs other focus |
| `social_dominance` | `synthetic_social_dominance` | dominance_score, initiation_rate | Lead vs follow tendency |
| `adaptiveness` | `synthetic_adaptive_communication` | style_adaptation, formality_matching | Style adaptation to partner |
| `attunement` | `synthetic_interpersonal_attunement` | sentiment_mirroring, emotional_responsiveness | Responsiveness to others |

### How Synthetic Features Are Calculated

Each synthetic feature combines multiple raw features with weighted averaging. For example:

**`communication_warmth`** = weighted combination of:
- `sentiment_mean` (normalized to 0-1) × 0.2
- `positive_ratio` × 0.2
- `empathy_score` × 0.2
- `support_ratio` × 0.15
- `support_reactivity` × 0.15
- `politeness_score` × 0.1

See `llm_synthetic_features.py` for full calculation details.

### System Prompt Generation

The personality vector is passed to the LLM with interpretation rules:
- Values near **1.0** = STRONG expression of trait
- Values near **0.5** = MODERATE/NEUTRAL expression
- Values near **0.0** = MINIMAL expression of trait

Each dimension includes specific behavioral instructions for high/low values.

---

## Known Issues and Solutions

### Emotion Ratios Often Zero
**Problem**: `emotion_joy_ratio`, `emotion_sadness_ratio`, etc. are often 0 because they rely on exact word matches from small lexicons.

**Solution**: The synthetic features use broader sentiment-based calculations instead:
- `synthetic_positivity_bias` uses `sentiment_mean` + `positive_ratio` + `negative_ratio`
- `synthetic_emotional_expressiveness` uses emoji, exclamation, intensity metrics

### Feature Name Consistency
All feature names now follow the pattern: `{category}_{feature_name}`
- `text_lexical_richness` (not `text_vocabulary_richness`)
- `sentiment_positive_ratio` (not `sentiment_positivity_ratio`)
- `behavioral_empathy_score` (not just `empathy`)

---

## Recommendations for Future Improvements


3. **User feedback loop**: Allow users to rate persona accuracy and adjust weights
4. **A/B testing**: Compare synthetic vs raw feature effectiveness for persona generation
