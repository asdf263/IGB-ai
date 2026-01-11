# Useless Features Audit - LLM Synthetic Feature Usage

## Summary
This document tracks "completely useless" calibration features (3+ violations) and their resolution status.

**Status**: ✅ ALL ISSUES RESOLVED - All useless features have been removed, replaced, or now have normalization functions.

---

## ✅ CHANGES MADE TO llm_synthetic_features.py

### Removed Features (Useless - No Viable Normalization):
1. **negative_ratio** - Removed from `_compute_positivity_bias()` (redundant with positive_ratio)
2. **politeness_score** - Removed from `_compute_warmth()` and `_compute_formality()`
3. **pos_noun_ratio** - Removed from `_compute_intellectual_engagement()`
4. **pos_interjection_ratio** - Removed from `_compute_emotional_expressiveness()` and `_compute_text_expressiveness()`

### Replaced Features:
1. **question_frequency** → **question_mark_ratio** in `_compute_intellectual_engagement()` and `_compute_curiosity_openness()`

### Weight Redistributions:
- `_compute_warmth()`: Redistributed politeness_score weight to other features
- `_compute_intellectual_engagement()`: Redistributed pos_noun_ratio weight
- `_compute_emotional_expressiveness()`: Redistributed pos_interjection_ratio weight
- `_compute_formality()`: Replaced politeness_score with stopword_ratio
- `_compute_curiosity_openness()`: Simplified to use question_mark_ratio only
- `_compute_positivity_bias()`: Simplified to sentiment_mean + positive_ratio only
- `_compute_text_expressiveness()`: Redistributed pos_interjection_ratio weight

---

## ✅ NORMALIZATION FUNCTIONS ADDED TO calibrated_normalizer.py

### Additional Usable Features (7 total):
1. **digit_ratio** - Using points 0.0, 0.75, 1.0
2. **emotional_intensity_mean** - Using points 0.0, 0.5, 1.0
3. **sentiment_consistency** - Using points 0.505, 0.671, 1.0
4. **question_frequency** - Recalibrated after fixing data (0.0, 0.5, 1.0)

---

## ✅ DATA FIXES

### batch6.json:
- Fixed `question_frequency` calibration data by adding missing `?` marks to question messages
- Recalibrated values: [0.0=0.0, 0.25=0.0, 0.5=0.6, 0.75=0.6, 1.0=1.0]

---

## 🚫 FEATURES NOT USED IN SYNTHETIC CALCULATIONS (Safe to Ignore)

These useless features are NOT used anywhere in the LLM pipeline:

1. circadian_afternoon_ratio, circadian_evening_ratio, circadian_morning_ratio, circadian_night_ratio
2. emotional_shift_frequency
3. pos_adj_ratio, pos_adp_ratio, pos_adv_ratio, pos_conj_ratio, pos_det_ratio, pos_part_ratio, pos_verb_ratio
4. pos_num_ratio, pos_pron_ratio

---

## Current Normalization Coverage

**Total calibrated features**: 32
- **Perfect (8)**: all_caps_word_ratio, elaboration_score, sentiment_max, sentiment_mean, sentiment_skewness, sentiment_std, sentiment_trend, sentiment_volatility
- **Can Work (17)**: answer_frequency, formality_score, hapax_legomena_ratio, initiation_rate, lexical_richness, neutral_ratio, positive_ratio, punctuation_ratio, response_rate, sentiment_min, sentiment_range, stopword_ratio, type_token_ratio, uppercase_ratio, weekday_ratio, weekend_ratio, whitespace_ratio
- **Additional Usable (7)**: digit_ratio, emotional_intensity_mean, sentiment_consistency, question_frequency
