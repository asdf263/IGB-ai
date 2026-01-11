# Sentiment Feature Calibration Data

This document contains synthetic conversational data for calibrating and normalizing embedding values for all Sentiment category vector components.

---

## 1. sentiment_mean

### VECTOR_NAME: sentiment_mean
### INTENSITY: 0.0 (Extremely Negative)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, the user expresses extremely negative sentiment throughout - complaints, frustration, disappointment, anger. At 1.0, the user expresses extremely positive sentiment - joy, excitement, gratitude, enthusiasm.

```json
{
  "messages": [
    {"sender": "user", "text": "This is the worst day ever. Everything is terrible.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry to hear that. What happened?", "timestamp": 1715234045},
    {"sender": "user", "text": "I hate everything about this situation. It's awful and frustrating.", "timestamp": 1715234120},
    {"sender": "bot", "text": "That sounds really difficult.", "timestamp": 1715234180},
    {"sender": "user", "text": "Nothing ever works out. I'm so disappointed and angry.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I understand you're upset.", "timestamp": 1715234360},
    {"sender": "user", "text": "This is horrible. I can't stand it anymore. So miserable.", "timestamp": 1715234500},
    {"sender": "bot", "text": "Is there anything I can do to help?", "timestamp": 1715234560},
    {"sender": "user", "text": "No. Everything is ruined. I'm furious and depressed.", "timestamp": 1715234700},
    {"sender": "bot", "text": "I'm here if you need to talk.", "timestamp": 1715234760}
  ]
}
```

**expected_embedding_signature**:
- High frequency of negative sentiment words: "worst", "terrible", "hate", "awful", "frustrated", "disappointed", "angry", "horrible", "miserable", "furious", "depressed", "ruined"
- Zero positive sentiment words
- Consistent negative tone across all user messages
- Should produce sentiment_mean near -1.0
- No emotional relief or positive breaks

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (maximally negative)
- No contradicting positive elements present
- Risk: None - this is clearly more negative than any mid-range sample would be
- Intensity appears appropriately extreme

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_mean
### INTENSITY: 0.5 (Mixed/Neutral)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Today was okay I guess. Had some good moments.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Tell me more.", "timestamp": 1715234060},
    {"sender": "user", "text": "Work was a bit stressful but I managed.", "timestamp": 1715234150},
    {"sender": "bot", "text": "That's understandable.", "timestamp": 1715234200},
    {"sender": "user", "text": "The weather was nice which was pleasant.", "timestamp": 1715234300},
    {"sender": "bot", "text": "That's good.", "timestamp": 1715234360},
    {"sender": "user", "text": "Had a minor issue with my car but it's fine now.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Glad it worked out.", "timestamp": 1715234500},
    {"sender": "user", "text": "Overall pretty average day, nothing special.", "timestamp": 1715234600},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Mix of mild positive and mild negative words
- Positive: "good", "nice", "pleasant", "fine"
- Negative: "stressful", "issue"
- Neutral: "okay", "average", "nothing special"
- Should produce sentiment_mean near 0.0
- Balanced emotional tone

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (neutral/mixed)
- Balance of positive and negative elements
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_mean
### INTENSITY: 1.0 (Extremely Positive)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is absolutely amazing! I'm so happy and excited!", "timestamp": 1715234000},
    {"sender": "bot", "text": "That's wonderful! What's got you so excited?", "timestamp": 1715234030},
    {"sender": "user", "text": "Everything is perfect! I love this so much! Best day ever!", "timestamp": 1715234090},
    {"sender": "bot", "text": "I'm glad to hear it!", "timestamp": 1715234120},
    {"sender": "user", "text": "I'm thrilled and grateful! This is fantastic and wonderful!", "timestamp": 1715234200},
    {"sender": "bot", "text": "Your enthusiasm is contagious!", "timestamp": 1715234230},
    {"sender": "user", "text": "I feel blessed and fortunate! Everything is awesome!", "timestamp": 1715234320},
    {"sender": "bot", "text": "That's great to hear!", "timestamp": 1715234350},
    {"sender": "user", "text": "So delighted! This is excellent and brilliant! I'm overjoyed!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234480}
  ]
}
```

**expected_embedding_signature**:
- High frequency of positive sentiment words: "amazing", "happy", "excited", "perfect", "love", "best", "thrilled", "grateful", "fantastic", "wonderful", "blessed", "fortunate", "awesome", "delighted", "excellent", "brilliant", "overjoyed"
- Zero negative sentiment words
- Consistent positive tone across all user messages
- Should produce sentiment_mean near +1.0
- Exclamation marks reinforce intensity

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximally positive)
- No contradicting negative elements present
- Risk: None - this is clearly more positive than any mid-range sample
- Intensity appears appropriately extreme

**flagged_for_review**: false

---

## 2. sentiment_std

### VECTOR_NAME: sentiment_std
### INTENSITY: 0.0 (No Variation - Consistent Sentiment)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, sentiment is completely consistent across all messages (no variation). At 1.0, sentiment varies wildly from extremely positive to extremely negative between messages.

```json
{
  "messages": [
    {"sender": "user", "text": "Things are okay I guess.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Just okay?", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, it's fine. Nothing special.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "It's alright. Pretty normal day.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Sounds uneventful.", "timestamp": 1715234360},
    {"sender": "user", "text": "Yeah, just average. Nothing to complain about.", "timestamp": 1715234450},
    {"sender": "bot", "text": "That's fair.", "timestamp": 1715234500},
    {"sender": "user", "text": "It's decent. Not bad, not great.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- All messages have neutral sentiment (near 0)
- Words like "okay", "fine", "alright", "normal", "average", "decent"
- No strong positive or negative words
- Standard deviation should be near 0
- Monotone emotional expression

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no variation)
- All messages maintain consistent neutral tone
- Risk: None - clearly less variable than any sample with emotional swings
- Intensity appears appropriately flat

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_std
### INTENSITY: 0.5 (Moderate Variation)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm feeling pretty good today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "That's nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Although this one thing is annoying me.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What's that?", "timestamp": 1715234200},
    {"sender": "user", "text": "It's fine, I'm happy overall.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Good to hear.", "timestamp": 1715234360},
    {"sender": "user", "text": "Just a bit frustrated with work.", "timestamp": 1715234450},
    {"sender": "bot", "text": "I understand.", "timestamp": 1715234500},
    {"sender": "user", "text": "But looking forward to the weekend!", "timestamp": 1715234600},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Moderate variation between positive and mildly negative
- Some positive: "good", "happy", "looking forward"
- Some negative: "annoying", "frustrated"
- Standard deviation should be moderate (~0.5)
- Natural emotional fluctuation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate variation)
- Neither flat nor extreme swings
- Risk: None - clearly between no variation and maximum variation
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_std
### INTENSITY: 1.0 (Maximum Variation - Emotional Rollercoaster)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I LOVE THIS! Best thing ever! So amazing!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wow, you seem excited!", "timestamp": 1715234030},
    {"sender": "user", "text": "Actually no, I hate it. This is terrible and awful.", "timestamp": 1715234100},
    {"sender": "bot", "text": "Oh, what changed?", "timestamp": 1715234130},
    {"sender": "user", "text": "Wait, I was wrong! It's fantastic! I'm thrilled!", "timestamp": 1715234200},
    {"sender": "bot", "text": "That's quite a shift.", "timestamp": 1715234230},
    {"sender": "user", "text": "No actually this is the worst. I'm so angry and frustrated.", "timestamp": 1715234320},
    {"sender": "bot", "text": "Are you okay?", "timestamp": 1715234350},
    {"sender": "user", "text": "Yes! Everything is wonderful! I'm so happy and grateful!", "timestamp": 1715234450},
    {"sender": "bot", "text": "You seem to be going through a lot of emotions.", "timestamp": 1715234500}
  ]
}
```

**expected_embedding_signature**:
- Alternating extreme positive and negative sentiment
- Positive words: "LOVE", "Best", "amazing", "fantastic", "thrilled", "wonderful", "happy", "grateful"
- Negative words: "hate", "terrible", "awful", "worst", "angry", "frustrated"
- Maximum standard deviation in sentiment scores
- Rapid emotional swings between messages

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximum variation)
- Clear alternation between extreme positive and negative
- Risk: None - obviously more variable than consistent samples
- Intensity appears appropriately volatile

**flagged_for_review**: false

---

## 3. sentiment_min

### VECTOR_NAME: sentiment_min
### INTENSITY: 0.0 (Minimum is Extremely Negative)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, the lowest sentiment message is extremely negative. At 1.0, even the lowest sentiment message is still positive.

```json
{
  "messages": [
    {"sender": "user", "text": "Today was pretty good overall.", "timestamp": 1715234000},
    {"sender": "bot", "text": "That's nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, had some nice moments.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234200},
    {"sender": "user", "text": "But then THIS HAPPENED AND I ABSOLUTELY HATE EVERYTHING. WORST THING EVER. I'M FURIOUS AND DEVASTATED AND MISERABLE.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Oh no, what went wrong?", "timestamp": 1715234360},
    {"sender": "user", "text": "It's fine now, I'm okay.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Glad you're feeling better.", "timestamp": 1715234500},
    {"sender": "user", "text": "Yeah, things are alright.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Good to hear.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- One message with extreme negative sentiment (the outburst)
- Other messages are neutral to mildly positive
- The minimum sentiment value should be near -1.0
- Key negative words in outburst: "HATE", "WORST", "FURIOUS", "DEVASTATED", "MISERABLE"
- ALL CAPS intensifies the negative minimum

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (extremely negative minimum)
- The outburst message clearly represents the minimum
- Risk: None - the minimum is clearly more negative than samples without such outbursts
- Intensity of minimum appears appropriately extreme

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_min
### INTENSITY: 0.5 (Minimum is Mildly Negative)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Today is going well!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, pretty happy about things.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234200},
    {"sender": "user", "text": "This part is a bit disappointing though.", "timestamp": 1715234300},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234360},
    {"sender": "user", "text": "It's okay, not a big deal.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234500},
    {"sender": "user", "text": "Overall still a good day.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Good to hear.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Most messages positive, one mildly negative
- Minimum message has "disappointing" - mildly negative
- Minimum sentiment should be around -0.3 to -0.5
- Not extreme negative, not positive
- Moderate low point

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (mildly negative minimum)
- The minimum is between extreme negative and positive
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_min
### INTENSITY: 1.0 (Minimum is Still Positive)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is absolutely amazing! Best day ever!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234030},
    {"sender": "user", "text": "I'm so thrilled and excited about everything!", "timestamp": 1715234100},
    {"sender": "bot", "text": "That's great!", "timestamp": 1715234130},
    {"sender": "user", "text": "Well, this part is just nice. Still good though.", "timestamp": 1715234200},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234230},
    {"sender": "user", "text": "But overall I'm really happy and grateful!", "timestamp": 1715234320},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234350},
    {"sender": "user", "text": "Everything is wonderful and fantastic!", "timestamp": 1715234450},
    {"sender": "bot", "text": "So glad to hear!", "timestamp": 1715234480}
  ]
}
```

**expected_embedding_signature**:
- All messages are positive, even the "lowest" one
- The minimum message ("just nice. Still good though") is still mildly positive
- Minimum sentiment should be near +0.2 to +0.5
- No negative words anywhere
- Consistent positive baseline

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (positive minimum)
- Even the least enthusiastic message is still positive
- Risk: None - minimum is clearly higher than samples with negative moments
- Intensity appears appropriately bounded

**flagged_for_review**: false

---

## 4. sentiment_max

### VECTOR_NAME: sentiment_max
### INTENSITY: 0.0 (Maximum is Still Negative)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, even the most positive message is still negative. At 1.0, the maximum sentiment is extremely positive.

```json
{
  "messages": [
    {"sender": "user", "text": "Everything is terrible. I hate this.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "It's awful and frustrating.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What's wrong?", "timestamp": 1715234200},
    {"sender": "user", "text": "Well, I guess it's not the absolute worst. Still bad though.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234360},
    {"sender": "user", "text": "But mostly everything is horrible and disappointing.", "timestamp": 1715234450},
    {"sender": "bot", "text": "That's tough.", "timestamp": 1715234500},
    {"sender": "user", "text": "I'm so miserable and upset about all of this.", "timestamp": 1715234600},
    {"sender": "bot", "text": "I understand.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- All messages are negative, even the "highest" one
- The maximum message ("not the absolute worst. Still bad though") is still negative
- Maximum sentiment should be near -0.2 to -0.5
- Dominant negative words: "terrible", "hate", "awful", "frustrating", "horrible", "disappointing", "miserable", "upset"
- No truly positive words

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (negative maximum)
- Even the most positive-leaning message is still negative
- Risk: None - maximum is clearly lower than samples with positive moments
- Intensity appears appropriately bounded

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_max
### INTENSITY: 0.5 (Maximum is Mildly Positive)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Things are okay today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Just okay?", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, nothing special.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "This part is pretty nice actually.", "timestamp": 1715234300},
    {"sender": "bot", "text": "That's good.", "timestamp": 1715234360},
    {"sender": "user", "text": "Back to normal now.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234500},
    {"sender": "user", "text": "Just regular stuff.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Most messages neutral, one mildly positive
- Maximum message has "pretty nice" - mildly positive
- Maximum sentiment should be around +0.3 to +0.5
- Not extreme positive, not negative
- Moderate high point

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (mildly positive maximum)
- The maximum is between negative and extreme positive
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_max
### INTENSITY: 1.0 (Maximum is Extremely Positive)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Things are okay today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Just okay?", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, pretty normal.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "OH MY GOD THIS IS THE BEST THING EVER!!! I'M SO INCREDIBLY HAPPY AND THRILLED AND EXCITED!!! ABSOLUTELY AMAZING WONDERFUL FANTASTIC!!!", "timestamp": 1715234300},
    {"sender": "bot", "text": "Wow! What happened?", "timestamp": 1715234330},
    {"sender": "user", "text": "Back to normal now. It's fine.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Quite a moment there.", "timestamp": 1715234500},
    {"sender": "user", "text": "Yeah, just regular stuff now.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- One message with extreme positive sentiment (the outburst)
- Other messages are neutral
- Maximum sentiment should be near +1.0
- Key positive words in outburst: "BEST", "HAPPY", "THRILLED", "EXCITED", "AMAZING", "WONDERFUL", "FANTASTIC"
- ALL CAPS and multiple exclamation marks intensify the maximum

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (extremely positive maximum)
- The outburst message clearly represents the maximum
- Risk: None - the maximum is clearly more positive than samples without such peaks
- Intensity of maximum appears appropriately extreme

**flagged_for_review**: false

---

## 5. sentiment_range

### VECTOR_NAME: sentiment_range
### INTENSITY: 0.0 (No Range - All Same Sentiment)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, all messages have the same sentiment (range = 0). At 1.0, messages span from extremely negative to extremely positive (range = 2).

```json
{
  "messages": [
    {"sender": "user", "text": "It's okay.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Just okay?", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, fine.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234200},
    {"sender": "user", "text": "Pretty normal.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234360},
    {"sender": "user", "text": "Nothing special.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234500},
    {"sender": "user", "text": "Just average.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- All messages have identical neutral sentiment
- No positive or negative words
- Range should be 0 or near 0
- Monotone emotional expression
- Words: "okay", "fine", "normal", "nothing special", "average"

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no range)
- All messages maintain identical neutral tone
- Risk: None - clearly less range than any sample with emotional variation
- Intensity appears appropriately flat

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_range
### INTENSITY: 0.5 (Moderate Range)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm feeling pretty good today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Yeah, things are going well.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234200},
    {"sender": "user", "text": "This part is a bit frustrating though.", "timestamp": 1715234300},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234360},
    {"sender": "user", "text": "It's okay now, feeling better.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234500},
    {"sender": "user", "text": "Overall a decent day.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Glad to hear.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Messages range from mildly positive to mildly negative
- Range should be around 1.0 (half of maximum)
- Positive: "good", "well", "better", "decent"
- Negative: "frustrating"
- Moderate emotional span

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate range)
- Neither flat nor full spectrum
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_range
### INTENSITY: 1.0 (Maximum Range - Full Spectrum)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "THIS IS THE ABSOLUTE WORST!!! I HATE EVERYTHING!!! SO FURIOUS AND MISERABLE AND DEVASTATED!!!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Oh no, what's wrong?", "timestamp": 1715234060},
    {"sender": "user", "text": "Everything is terrible awful horrible.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234200},
    {"sender": "user", "text": "It's okay I guess.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Feeling better?", "timestamp": 1715234360},
    {"sender": "user", "text": "Actually yes! Things are looking up!", "timestamp": 1715234450},
    {"sender": "bot", "text": "That's good!", "timestamp": 1715234500},
    {"sender": "user", "text": "THIS IS THE BEST DAY EVER!!! I'M SO INCREDIBLY HAPPY AND THRILLED!!! ABSOLUTELY AMAZING WONDERFUL PERFECT!!!", "timestamp": 1715234600},
    {"sender": "bot", "text": "Quite a turnaround!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Messages span from extremely negative (-1.0) to extremely positive (+1.0)
- Range should be near 2.0 (maximum possible)
- Extreme negative: "WORST", "HATE", "FURIOUS", "MISERABLE", "DEVASTATED", "terrible", "awful", "horrible"
- Extreme positive: "BEST", "HAPPY", "THRILLED", "AMAZING", "WONDERFUL", "PERFECT"
- Clear progression from negative to positive

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximum range)
- Full emotional spectrum represented
- Risk: None - range is clearly larger than any sample without extremes
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 6. sentiment_skewness

### VECTOR_NAME: sentiment_skewness
### INTENSITY: 0.0 (Negative Skew - Most Messages Positive, Few Negative Outliers)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, distribution is negatively skewed (most positive, few negative outliers). At 1.0, distribution is positively skewed (most negative, few positive outliers).

```json
{
  "messages": [
    {"sender": "user", "text": "This is great! I love it!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234060},
    {"sender": "user", "text": "So happy and excited!", "timestamp": 1715234150},
    {"sender": "bot", "text": "That's nice!", "timestamp": 1715234200},
    {"sender": "user", "text": "Everything is amazing!", "timestamp": 1715234300},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm thrilled!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234500},
    {"sender": "user", "text": "But this one thing is absolutely terrible and I hate it.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Oh no.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Most messages are positive (4 out of 5 user messages)
- One negative outlier at the end
- Negative skewness (tail extends toward negative)
- Mean is pulled down by the outlier
- Median is higher than mean

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (negative skew)
- Clear pattern of mostly positive with negative outlier
- Risk: None - skew direction is clearly negative
- Intensity appears appropriately skewed

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_skewness
### INTENSITY: 0.5 (Symmetric Distribution - No Skew)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is great!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "This is terrible.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Oh no.", "timestamp": 1715234200},
    {"sender": "user", "text": "Things are okay.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm happy about this.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234500},
    {"sender": "user", "text": "But upset about that.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Equal mix of positive and negative messages
- Symmetric distribution around neutral
- Skewness should be near 0
- Mean equals median
- Balanced emotional expression

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (no skew)
- Equal positive and negative representation
- Risk: None - clearly between skewed extremes
- Intensity appears appropriately balanced

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_skewness
### INTENSITY: 1.0 (Positive Skew - Most Messages Negative, Few Positive Outliers)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is terrible. I hate it.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "So frustrated and upset.", "timestamp": 1715234150},
    {"sender": "bot", "text": "That's tough.", "timestamp": 1715234200},
    {"sender": "user", "text": "Everything is awful.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I understand.", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm miserable.", "timestamp": 1715234450},
    {"sender": "bot", "text": "I'm here for you.", "timestamp": 1715234500},
    {"sender": "user", "text": "But this one thing is absolutely amazing and I love it!", "timestamp": 1715234600},
    {"sender": "bot", "text": "That's nice!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Most messages are negative (4 out of 5 user messages)
- One positive outlier at the end
- Positive skewness (tail extends toward positive)
- Mean is pulled up by the outlier
- Median is lower than mean

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (positive skew)
- Clear pattern of mostly negative with positive outlier
- Risk: None - skew direction is clearly positive
- Intensity appears appropriately skewed

**flagged_for_review**: false

---

## 7. positive_ratio

### VECTOR_NAME: positive_ratio
### INTENSITY: 0.0 (No Positive Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, zero messages are positive. At 1.0, all messages are positive.

```json
{
  "messages": [
    {"sender": "user", "text": "This is terrible.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "I hate everything about this.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What's wrong?", "timestamp": 1715234200},
    {"sender": "user", "text": "It's awful and frustrating.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I understand.", "timestamp": 1715234360},
    {"sender": "user", "text": "So disappointed and upset.", "timestamp": 1715234450},
    {"sender": "bot", "text": "That's tough.", "timestamp": 1715234500},
    {"sender": "user", "text": "Everything is horrible.", "timestamp": 1715234600},
    {"sender": "bot", "text": "I'm here.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Zero positive sentiment words
- All user messages are negative
- positive_ratio should be 0.0
- Negative words: "terrible", "hate", "awful", "frustrating", "disappointed", "upset", "horrible"

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no positive)
- No positive messages present
- Risk: None - clearly 0% positive
- Intensity appears appropriately zero

**flagged_for_review**: false

---

### VECTOR_NAME: positive_ratio
### INTENSITY: 0.5 (Half Positive Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is great!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Things are okay.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "I'm happy about this.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234360},
    {"sender": "user", "text": "That part is fine.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234500},
    {"sender": "user", "text": "Overall pretty good!", "timestamp": 1715234600},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Mix of positive and neutral messages
- positive_ratio should be around 0.5
- Some positive: "great", "happy", "good"
- Some neutral: "okay", "fine"
- Half positive representation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (half positive)
- Balance of positive and neutral
- Risk: None - clearly between 0% and 100%
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: positive_ratio
### INTENSITY: 1.0 (All Positive Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is amazing!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234030},
    {"sender": "user", "text": "I love everything about this!", "timestamp": 1715234100},
    {"sender": "bot", "text": "That's great!", "timestamp": 1715234130},
    {"sender": "user", "text": "It's fantastic and wonderful!", "timestamp": 1715234200},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234230},
    {"sender": "user", "text": "So happy and excited!", "timestamp": 1715234320},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234350},
    {"sender": "user", "text": "Everything is perfect!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Brilliant!", "timestamp": 1715234480}
  ]
}
```

**expected_embedding_signature**:
- All user messages are positive
- positive_ratio should be 1.0
- Positive words: "amazing", "love", "fantastic", "wonderful", "happy", "excited", "perfect"
- Zero negative words

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (all positive)
- All messages are positive
- Risk: None - clearly 100% positive
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 8. negative_ratio

### VECTOR_NAME: negative_ratio
### INTENSITY: 0.0 (No Negative Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, zero messages are negative. At 1.0, all messages are negative.

```json
{
  "messages": [
    {"sender": "user", "text": "This is great!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234030},
    {"sender": "user", "text": "I'm so happy!", "timestamp": 1715234100},
    {"sender": "bot", "text": "That's lovely!", "timestamp": 1715234130},
    {"sender": "user", "text": "Everything is fine and good.", "timestamp": 1715234200},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234230},
    {"sender": "user", "text": "I feel okay about this.", "timestamp": 1715234320},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234350},
    {"sender": "user", "text": "Things are pleasant.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234480}
  ]
}
```

**expected_embedding_signature**:
- Zero negative sentiment words
- All user messages are positive or neutral
- negative_ratio should be 0.0
- Positive/neutral words: "great", "happy", "fine", "good", "okay", "pleasant"

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no negative)
- No negative messages present
- Risk: None - clearly 0% negative
- Intensity appears appropriately zero

**flagged_for_review**: false

---

### VECTOR_NAME: negative_ratio
### INTENSITY: 0.5 (Half Negative Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is frustrating.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "Things are okay.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "That part is annoying.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234360},
    {"sender": "user", "text": "It's fine I guess.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234500},
    {"sender": "user", "text": "Overall pretty average.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Mix of negative and neutral messages
- negative_ratio should be around 0.5
- Some negative: "frustrating", "annoying"
- Some neutral: "okay", "fine", "average"
- Half negative representation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (half negative)
- Balance of negative and neutral
- Risk: None - clearly between 0% and 100%
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: negative_ratio
### INTENSITY: 1.0 (All Negative Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is terrible.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "I hate this so much.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234200},
    {"sender": "user", "text": "Everything is awful.", "timestamp": 1715234300},
    {"sender": "bot", "text": "That's tough.", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm so frustrated and angry.", "timestamp": 1715234450},
    {"sender": "bot", "text": "I understand.", "timestamp": 1715234500},
    {"sender": "user", "text": "This is the worst.", "timestamp": 1715234600},
    {"sender": "bot", "text": "I'm here.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- All user messages are negative
- negative_ratio should be 1.0
- Negative words: "terrible", "hate", "awful", "frustrated", "angry", "worst"
- Zero positive words

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (all negative)
- All messages are negative
- Risk: None - clearly 100% negative
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 9. neutral_ratio

### VECTOR_NAME: neutral_ratio
### INTENSITY: 0.0 (No Neutral Messages - All Emotional)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, zero messages are neutral (all are strongly positive or negative). At 1.0, all messages are neutral.

```json
{
  "messages": [
    {"sender": "user", "text": "I LOVE this! It's AMAZING!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234030},
    {"sender": "user", "text": "I HATE that! It's TERRIBLE!", "timestamp": 1715234100},
    {"sender": "bot", "text": "Oh no.", "timestamp": 1715234130},
    {"sender": "user", "text": "This is WONDERFUL and FANTASTIC!", "timestamp": 1715234200},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234230},
    {"sender": "user", "text": "That's AWFUL and HORRIBLE!", "timestamp": 1715234320},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234350},
    {"sender": "user", "text": "But THIS is BRILLIANT and PERFECT!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234480}
  ]
}
```

**expected_embedding_signature**:
- All user messages are strongly emotional (positive or negative)
- neutral_ratio should be 0.0
- Strong positive: "LOVE", "AMAZING", "WONDERFUL", "FANTASTIC", "BRILLIANT", "PERFECT"
- Strong negative: "HATE", "TERRIBLE", "AWFUL", "HORRIBLE"
- No neutral/bland messages

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no neutral)
- All messages are emotionally charged
- Risk: None - clearly 0% neutral
- Intensity appears appropriately zero

**flagged_for_review**: false

---

### VECTOR_NAME: neutral_ratio
### INTENSITY: 0.5 (Half Neutral Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is great!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Okay.", "timestamp": 1715234150},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "I'm happy about this.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234360},
    {"sender": "user", "text": "Sure.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234500},
    {"sender": "user", "text": "Fine.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Mix of emotional and neutral messages
- neutral_ratio should be around 0.5
- Some emotional: "great", "happy"
- Some neutral: "Okay", "Sure", "Fine"
- Half neutral representation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (half neutral)
- Balance of emotional and neutral
- Risk: None - clearly between 0% and 100%
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: neutral_ratio
### INTENSITY: 1.0 (All Neutral Messages)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Okay.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234060},
    {"sender": "user", "text": "Sure.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234200},
    {"sender": "user", "text": "Fine.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234360},
    {"sender": "user", "text": "Yeah.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234500},
    {"sender": "user", "text": "Mhm.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Okay.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- All user messages are neutral
- neutral_ratio should be 1.0
- Neutral words: "Okay", "Sure", "Fine", "Yeah", "Mhm"
- Zero positive or negative words
- Minimal engagement, flat affect

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (all neutral)
- All messages are emotionally flat
- Risk: None - clearly 100% neutral
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 10. sentiment_volatility

### VECTOR_NAME: sentiment_volatility
### INTENSITY: 0.0 (No Volatility - Stable Sentiment)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, sentiment doesn't change between messages. At 1.0, sentiment swings dramatically between every message.

```json
{
  "messages": [
    {"sender": "user", "text": "I'm happy today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "That's nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Yes, feeling good.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234200},
    {"sender": "user", "text": "Things are great.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm pleased.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234500},
    {"sender": "user", "text": "Everything is nice.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Sentiment stays consistently positive across all messages
- No changes between messages
- Volatility should be 0.0
- Stable positive words: "happy", "good", "great", "pleased", "nice"
- No emotional swings

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no volatility)
- Sentiment is stable throughout
- Risk: None - clearly less volatile than any sample with changes
- Intensity appears appropriately stable

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_volatility
### INTENSITY: 0.5 (Moderate Volatility)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm feeling good today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "This part is frustrating.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234200},
    {"sender": "user", "text": "It's okay now.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234360},
    {"sender": "user", "text": "Actually pretty happy!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234500},
    {"sender": "user", "text": "Things are fine.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Moderate swings between positive, neutral, and mildly negative
- Volatility should be around 1.0 (half of maximum)
- Some variation but not extreme
- Natural emotional fluctuation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate volatility)
- Neither stable nor extreme swings
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_volatility
### INTENSITY: 1.0 (Maximum Volatility - Constant Swings)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I LOVE THIS! AMAZING!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234020},
    {"sender": "user", "text": "Actually I HATE it! TERRIBLE!", "timestamp": 1715234060},
    {"sender": "bot", "text": "Oh.", "timestamp": 1715234080},
    {"sender": "user", "text": "No wait it's WONDERFUL! FANTASTIC!", "timestamp": 1715234120},
    {"sender": "bot", "text": "Okay.", "timestamp": 1715234140},
    {"sender": "user", "text": "Ugh no it's AWFUL! HORRIBLE!", "timestamp": 1715234180},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "Actually it's PERFECT! BRILLIANT!", "timestamp": 1715234240},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234260}
  ]
}
```

**expected_embedding_signature**:
- Sentiment swings from extreme positive to extreme negative every message
- Maximum volatility (average change near 2.0)
- Alternating: positive → negative → positive → negative → positive
- Rapid timestamp changes indicate emotional instability
- ALL CAPS intensifies each swing

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximum volatility)
- Every message is a dramatic swing from the previous
- Risk: None - clearly more volatile than any stable sample
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 11. sentiment_trend

### VECTOR_NAME: sentiment_trend
### INTENSITY: 0.0 (Negative Trend - Getting Worse)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, sentiment trends downward (starts positive, ends negative). At 1.0, sentiment trends upward (starts negative, ends positive).

```json
{
  "messages": [
    {"sender": "user", "text": "This is amazing! I love it!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234060},
    {"sender": "user", "text": "It's really great!", "timestamp": 1715234150},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234200},
    {"sender": "user", "text": "Hmm, it's okay I guess.", "timestamp": 1715234300},
    {"sender": "bot", "text": "What changed?", "timestamp": 1715234360},
    {"sender": "user", "text": "Actually it's not that good.", "timestamp": 1715234450},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234500},
    {"sender": "user", "text": "This is pretty bad actually.", "timestamp": 1715234600},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234660},
    {"sender": "user", "text": "I hate this. It's terrible.", "timestamp": 1715234750},
    {"sender": "bot", "text": "That's unfortunate.", "timestamp": 1715234800}
  ]
}
```

**expected_embedding_signature**:
- Clear downward trajectory: positive → neutral → negative
- Negative slope in sentiment over time
- Early: "amazing", "love", "great"
- Middle: "okay", "not that good"
- Late: "bad", "hate", "terrible"
- Trend should be strongly negative

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (negative trend)
- Clear deterioration of sentiment over time
- Risk: None - clearly downward trend
- Intensity appears appropriately negative

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_trend
### INTENSITY: 0.5 (No Trend - Flat)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "Things are okay.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234060},
    {"sender": "user", "text": "Pretty normal day.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234200},
    {"sender": "user", "text": "It's fine.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234360},
    {"sender": "user", "text": "Just average.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234500},
    {"sender": "user", "text": "Nothing special.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- No clear trend direction
- Sentiment stays relatively flat throughout
- Trend slope should be near 0
- Consistent neutral tone
- No improvement or deterioration

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (no trend)
- Neither improving nor worsening
- Risk: None - clearly between extremes
- Intensity appears appropriately flat

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_trend
### INTENSITY: 1.0 (Positive Trend - Getting Better)
### CONVERSATION_LENGTH: 12
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "This is terrible. I hate it.", "timestamp": 1715234000},
    {"sender": "bot", "text": "I'm sorry.", "timestamp": 1715234060},
    {"sender": "user", "text": "It's really bad.", "timestamp": 1715234150},
    {"sender": "bot", "text": "What's wrong?", "timestamp": 1715234200},
    {"sender": "user", "text": "Well, maybe it's not that bad.", "timestamp": 1715234300},
    {"sender": "bot", "text": "That's better.", "timestamp": 1715234360},
    {"sender": "user", "text": "Actually it's okay.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234500},
    {"sender": "user", "text": "This is pretty nice actually.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234660},
    {"sender": "user", "text": "I love this! It's amazing!", "timestamp": 1715234750},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234800}
  ]
}
```

**expected_embedding_signature**:
- Clear upward trajectory: negative → neutral → positive
- Positive slope in sentiment over time
- Early: "terrible", "hate", "bad"
- Middle: "not that bad", "okay"
- Late: "nice", "love", "amazing"
- Trend should be strongly positive

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (positive trend)
- Clear improvement of sentiment over time
- Risk: None - clearly upward trend
- Intensity appears appropriately positive

**flagged_for_review**: false

---

## 12. emotional_intensity_mean

### VECTOR_NAME: emotional_intensity_mean
### INTENSITY: 0.0 (No Intensity - Flat Affect)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, messages have no emotional intensity (no intensifiers, no punctuation emphasis). At 1.0, messages are extremely intense (many intensifiers, exclamation marks, caps).

```json
{
  "messages": [
    {"sender": "user", "text": "okay", "timestamp": 1715234000},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234060},
    {"sender": "user", "text": "sure", "timestamp": 1715234150},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234200},
    {"sender": "user", "text": "fine", "timestamp": 1715234300},
    {"sender": "bot", "text": "Understood.", "timestamp": 1715234360},
    {"sender": "user", "text": "yeah", "timestamp": 1715234450},
    {"sender": "bot", "text": "Got it.", "timestamp": 1715234500},
    {"sender": "user", "text": "mhm", "timestamp": 1715234600},
    {"sender": "bot", "text": "Okay.", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- No intensifiers (very, really, extremely, etc.)
- No exclamation marks
- No caps
- Minimal word count
- emotional_intensity_mean should be near 0.0
- Flat, disengaged responses

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no intensity)
- Complete absence of emotional markers
- Risk: None - clearly less intense than any expressive sample
- Intensity appears appropriately minimal

**flagged_for_review**: false

---

### VECTOR_NAME: emotional_intensity_mean
### INTENSITY: 0.5 (Moderate Intensity)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm pretty happy about this!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "It's really good.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234200},
    {"sender": "user", "text": "I'm quite pleased.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234360},
    {"sender": "user", "text": "This is very nice!", "timestamp": 1715234450},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234500},
    {"sender": "user", "text": "Really enjoying it.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Some intensifiers: "pretty", "really", "quite", "very"
- Some exclamation marks but not excessive
- No ALL CAPS
- Moderate word count
- emotional_intensity_mean should be around 0.5
- Engaged but not extreme

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate intensity)
- Some emotional markers but not overwhelming
- Risk: None - clearly between flat and extreme
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: emotional_intensity_mean
### INTENSITY: 1.0 (Maximum Intensity - Extremely Expressive)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "OH MY GOD THIS IS SO INCREDIBLY ABSOLUTELY AMAZING!!!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Wow!", "timestamp": 1715234020},
    {"sender": "user", "text": "I AM EXTREMELY TOTALLY COMPLETELY THRILLED!!!", "timestamp": 1715234060},
    {"sender": "bot", "text": "That's great!", "timestamp": 1715234080},
    {"sender": "user", "text": "THIS IS REALLY REALLY REALLY WONDERFUL!!!", "timestamp": 1715234120},
    {"sender": "bot", "text": "Lovely!", "timestamp": 1715234140},
    {"sender": "user", "text": "I'M SO SO SO INCREDIBLY HAPPY RIGHT NOW!!!", "timestamp": 1715234180},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234200},
    {"sender": "user", "text": "ABSOLUTELY UTTERLY COMPLETELY FANTASTIC!!!", "timestamp": 1715234240},
    {"sender": "bot", "text": "Brilliant!", "timestamp": 1715234260}
  ]
}
```

**expected_embedding_signature**:
- Maximum intensifiers: "so", "incredibly", "absolutely", "extremely", "totally", "completely", "really", "utterly"
- Multiple exclamation marks (!!!)
- ALL CAPS throughout
- Repeated intensifiers for emphasis
- emotional_intensity_mean should be near 1.0

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximum intensity)
- Every possible intensity marker is used
- Risk: None - clearly more intense than any flat sample
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 13. emotional_shift_frequency

### VECTOR_NAME: emotional_shift_frequency
### INTENSITY: 0.0 (No Shifts - Stable Emotion)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, no significant emotional shifts occur. At 1.0, every transition between messages is a significant emotional shift.

```json
{
  "messages": [
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Still happy.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234200},
    {"sender": "user", "text": "Yep, happy.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234360},
    {"sender": "user", "text": "Feeling good.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234500},
    {"sender": "user", "text": "All good here.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- No emotional shifts between messages
- Consistent positive sentiment throughout
- emotional_shift_frequency should be 0.0
- Same emotional state maintained
- Stable, predictable pattern

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no shifts)
- No transitions cross the significance threshold
- Risk: None - clearly fewer shifts than any volatile sample
- Intensity appears appropriately stable

**flagged_for_review**: false

---

### VECTOR_NAME: emotional_shift_frequency
### INTENSITY: 0.5 (Moderate Shifts)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm happy today.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Still feeling good.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234200},
    {"sender": "user", "text": "This part is frustrating though.", "timestamp": 1715234300},
    {"sender": "bot", "text": "What happened?", "timestamp": 1715234360},
    {"sender": "user", "text": "It's okay now.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234500},
    {"sender": "user", "text": "Back to feeling happy!", "timestamp": 1715234600},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Some emotional shifts but not every message
- Shifts: happy → good → frustrated → okay → happy
- emotional_shift_frequency should be around 0.5
- Some transitions cross threshold, some don't
- Natural emotional variation

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate shifts)
- Neither completely stable nor constantly shifting
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: emotional_shift_frequency
### INTENSITY: 1.0 (Maximum Shifts - Every Message Changes)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm so happy!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234020},
    {"sender": "user", "text": "Now I'm furious!", "timestamp": 1715234060},
    {"sender": "bot", "text": "Oh no.", "timestamp": 1715234080},
    {"sender": "user", "text": "Wait, I'm excited!", "timestamp": 1715234120},
    {"sender": "bot", "text": "Okay.", "timestamp": 1715234140},
    {"sender": "user", "text": "Actually I'm devastated.", "timestamp": 1715234180},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "No, I'm thrilled!", "timestamp": 1715234240},
    {"sender": "bot", "text": "Alright.", "timestamp": 1715234260}
  ]
}
```

**expected_embedding_signature**:
- Every user message is a significant shift from the previous
- Alternating: happy → furious → excited → devastated → thrilled
- emotional_shift_frequency should be 1.0
- Maximum transitions per opportunity
- Rapid emotional changes

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (maximum shifts)
- Every transition is a significant emotional shift
- Risk: None - clearly more shifts than any stable sample
- Intensity appears appropriately maximal

**flagged_for_review**: false

---

## 14. sentiment_consistency

### VECTOR_NAME: sentiment_consistency
### INTENSITY: 0.0 (No Consistency - Highly Variable)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300
### BEHAVIORAL_DESCRIPTION: At 0.0, sentiment is highly inconsistent (high std, low consistency score). At 1.0, sentiment is perfectly consistent (low std, high consistency score).

```json
{
  "messages": [
    {"sender": "user", "text": "AMAZING! I LOVE IT!", "timestamp": 1715234000},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234020},
    {"sender": "user", "text": "TERRIBLE! I HATE IT!", "timestamp": 1715234060},
    {"sender": "bot", "text": "Oh.", "timestamp": 1715234080},
    {"sender": "user", "text": "WONDERFUL! FANTASTIC!", "timestamp": 1715234120},
    {"sender": "bot", "text": "Nice.", "timestamp": 1715234140},
    {"sender": "user", "text": "AWFUL! HORRIBLE!", "timestamp": 1715234180},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234200},
    {"sender": "user", "text": "PERFECT! BRILLIANT!", "timestamp": 1715234240},
    {"sender": "bot", "text": "Okay.", "timestamp": 1715234260}
  ]
}
```

**expected_embedding_signature**:
- Maximum standard deviation in sentiment
- sentiment_consistency = 1/(1+std) should be near 0.0
- Wild swings between extreme positive and negative
- No predictable pattern
- High variance

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.0 (no consistency)
- Maximum variability in sentiment
- Risk: None - clearly less consistent than any stable sample
- Intensity appears appropriately inconsistent

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_consistency
### INTENSITY: 0.5 (Moderate Consistency)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm feeling good.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "Pretty happy today.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234200},
    {"sender": "user", "text": "Things are okay.", "timestamp": 1715234300},
    {"sender": "bot", "text": "I see.", "timestamp": 1715234360},
    {"sender": "user", "text": "Feeling alright.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Good.", "timestamp": 1715234500},
    {"sender": "user", "text": "Yeah, pretty good.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Moderate standard deviation in sentiment
- sentiment_consistency = 1/(1+std) should be around 0.5
- Some variation but not extreme
- Mostly positive with some neutral
- Moderate variance

**consistency_verification**:
- Content realistically corresponds to INTENSITY 0.5 (moderate consistency)
- Some variability but not wild swings
- Risk: None - clearly between extremes
- Intensity appears appropriately moderate

**flagged_for_review**: false

---

### VECTOR_NAME: sentiment_consistency
### INTENSITY: 1.0 (Perfect Consistency - No Variation)
### CONVERSATION_LENGTH: 10
### TIMESTAMP_START: 1715234000
### TIMESTAMP_VARIABILITY: 300

```json
{
  "messages": [
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234000},
    {"sender": "bot", "text": "Nice!", "timestamp": 1715234060},
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234150},
    {"sender": "bot", "text": "Good!", "timestamp": 1715234200},
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234300},
    {"sender": "bot", "text": "Great!", "timestamp": 1715234360},
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234450},
    {"sender": "bot", "text": "Wonderful!", "timestamp": 1715234500},
    {"sender": "user", "text": "I'm happy.", "timestamp": 1715234600},
    {"sender": "bot", "text": "Excellent!", "timestamp": 1715234660}
  ]
}
```

**expected_embedding_signature**:
- Zero standard deviation in sentiment
- sentiment_consistency = 1/(1+std) should be 1.0
- Identical sentiment in every message
- Perfect predictability
- Zero variance

**consistency_verification**:
- Content realistically corresponds to INTENSITY 1.0 (perfect consistency)
- Zero variability in sentiment
- Risk: None - clearly more consistent than any variable sample
- Intensity appears appropriately consistent

**flagged_for_review**: false

---

# Summary

| Feature | 0.0 Behavior | 0.5 Behavior | 1.0 Behavior |
|---------|--------------|--------------|--------------|
| sentiment_mean | Extremely negative | Mixed/Neutral | Extremely positive |
| sentiment_std | No variation | Moderate variation | Maximum variation |
| sentiment_min | Extremely negative minimum | Mildly negative minimum | Positive minimum |
| sentiment_max | Negative maximum | Mildly positive maximum | Extremely positive maximum |
| sentiment_range | No range (0) | Moderate range (~1.0) | Full spectrum (2.0) |
| sentiment_skewness | Negative skew | Symmetric (no skew) | Positive skew |
| positive_ratio | 0% positive | 50% positive | 100% positive |
| negative_ratio | 0% negative | 50% negative | 100% negative |
| neutral_ratio | 0% neutral | 50% neutral | 100% neutral |
| sentiment_volatility | No volatility | Moderate volatility | Maximum volatility |
| sentiment_trend | Negative trend | No trend (flat) | Positive trend |
| emotional_intensity_mean | No intensity | Moderate intensity | Maximum intensity |
| emotional_shift_frequency | No shifts | Moderate shifts | Maximum shifts |
| sentiment_consistency | No consistency | Moderate consistency | Perfect consistency |

---

# Normalization Formula (3-Point Linear Interpolation)

For any raw feature value `x`, given three anchor points:
- `v_0` = raw value at intensity 0.0
- `v_0.5` = raw value at intensity 0.5
- `v_1` = raw value at intensity 1.0

**Piecewise Linear Normalization (assuming uniform distribution):**

```
if x <= v_0.5:
    normalized = 0.5 * (x - v_0) / (v_0.5 - v_0)
else:
    normalized = 0.5 + 0.5 * (x - v_0.5) / (v_1 - v_0.5)

normalized = clamp(normalized, 0.0, 1.0)
```

**Single Linear Formula (simplified, assumes linear relationship):**

```
normalized = (x - v_0) / (v_1 - v_0)
normalized = clamp(normalized, 0.0, 1.0)
```

**Validation using 0.5 anchor:**
- Expected: `normalize(v_0.5)` should equal `0.5 ± 0.1`
- If deviation > 0.1, the feature may have non-linear scaling
