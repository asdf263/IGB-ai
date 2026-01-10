"""
Linguistic Feature Extraction Module with spaCy
Extracts ~30 linguistic and grammatical features using spaCy NLP
"""
import numpy as np
from typing import List, Dict, Any
from collections import Counter


class LinguisticFeatureExtractorSpacy:
    """Extracts linguistic features using spaCy NLP pipeline."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = None
        self.model_name = model_name
        self._init_spacy()
        
        self.feature_names = [
            'pos_noun_ratio',
            'pos_verb_ratio',
            'pos_adj_ratio',
            'pos_adv_ratio',
            'pos_pronoun_ratio',
            'pos_preposition_ratio',
            'pos_conjunction_ratio',
            'pos_interjection_ratio',
            'pos_determiner_ratio',
            'pos_auxiliary_ratio',
            'first_person_ratio',
            'second_person_ratio',
            'third_person_ratio',
            'past_tense_ratio',
            'present_tense_ratio',
            'future_tense_ratio',
            'modal_verb_ratio',
            'named_entity_count',
            'entity_person_ratio',
            'entity_org_ratio',
            'entity_location_ratio',
            'avg_dependency_depth',
            'avg_noun_chunks',
            'subordinate_clause_ratio',
            'passive_voice_ratio',
            'negation_ratio',
            'question_ratio',
            'exclamation_ratio',
            'avg_sentence_length',
            'readability_score'
        ]
    
    def _init_spacy(self):
        """Initialize spaCy model."""
        try:
            import spacy
            try:
                self.nlp = spacy.load(self.model_name)
            except OSError:
                print(f"Downloading spaCy model {self.model_name}...")
                from spacy.cli import download
                download(self.model_name)
                self.nlp = spacy.load(self.model_name)
        except ImportError:
            print("spaCy not installed, linguistic features will be limited")
            self.nlp = None
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all linguistic features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        if self.nlp is None:
            return self._extract_basic(texts)
        
        all_text = ' '.join(texts)
        doc = self.nlp(all_text)
        
        features = {}
        
        pos_features = self._extract_pos_features(doc)
        features.update(pos_features)
        
        pronoun_features = self._extract_pronoun_features(doc)
        features.update(pronoun_features)
        
        tense_features = self._extract_tense_features(doc)
        features.update(tense_features)
        
        entity_features = self._extract_entity_features(doc)
        features.update(entity_features)
        
        syntax_features = self._extract_syntax_features(doc)
        features.update(syntax_features)
        
        sentence_features = self._extract_sentence_features(texts)
        features.update(sentence_features)
        
        return features
    
    def _extract_pos_features(self, doc) -> Dict[str, float]:
        """Extract POS tag distribution features."""
        pos_counts = Counter(token.pos_ for token in doc)
        total = len(doc) or 1
        
        return {
            'pos_noun_ratio': pos_counts.get('NOUN', 0) / total,
            'pos_verb_ratio': pos_counts.get('VERB', 0) / total,
            'pos_adj_ratio': pos_counts.get('ADJ', 0) / total,
            'pos_adv_ratio': pos_counts.get('ADV', 0) / total,
            'pos_pronoun_ratio': pos_counts.get('PRON', 0) / total,
            'pos_preposition_ratio': pos_counts.get('ADP', 0) / total,
            'pos_conjunction_ratio': (pos_counts.get('CCONJ', 0) + pos_counts.get('SCONJ', 0)) / total,
            'pos_interjection_ratio': pos_counts.get('INTJ', 0) / total,
            'pos_determiner_ratio': pos_counts.get('DET', 0) / total,
            'pos_auxiliary_ratio': pos_counts.get('AUX', 0) / total,
        }
    
    def _extract_pronoun_features(self, doc) -> Dict[str, float]:
        """Extract pronoun person features."""
        first_person = {'i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves'}
        second_person = {'you', 'your', 'yours', 'yourself', 'yourselves'}
        third_person = {'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                       'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'}
        
        pronouns = [token.text.lower() for token in doc if token.pos_ == 'PRON']
        total = len(pronouns) or 1
        
        return {
            'first_person_ratio': sum(1 for p in pronouns if p in first_person) / total,
            'second_person_ratio': sum(1 for p in pronouns if p in second_person) / total,
            'third_person_ratio': sum(1 for p in pronouns if p in third_person) / total,
        }
    
    def _extract_tense_features(self, doc) -> Dict[str, float]:
        """Extract verb tense features."""
        verbs = [token for token in doc if token.pos_ in ('VERB', 'AUX')]
        total = len(verbs) or 1
        
        past = sum(1 for v in verbs if v.tag_ in ('VBD', 'VBN'))
        present = sum(1 for v in verbs if v.tag_ in ('VBP', 'VBZ', 'VBG'))
        
        modal_verbs = {'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'}
        modals = sum(1 for v in verbs if v.text.lower() in modal_verbs)
        future = sum(1 for v in verbs if v.text.lower() in ('will', 'shall', "'ll"))
        
        return {
            'past_tense_ratio': past / total,
            'present_tense_ratio': present / total,
            'future_tense_ratio': future / total,
            'modal_verb_ratio': modals / total,
        }
    
    def _extract_entity_features(self, doc) -> Dict[str, float]:
        """Extract named entity features."""
        entities = list(doc.ents)
        total = len(entities) or 1
        
        entity_types = Counter(ent.label_ for ent in entities)
        
        return {
            'named_entity_count': float(len(entities)),
            'entity_person_ratio': entity_types.get('PERSON', 0) / total,
            'entity_org_ratio': entity_types.get('ORG', 0) / total,
            'entity_location_ratio': (entity_types.get('GPE', 0) + entity_types.get('LOC', 0)) / total,
        }
    
    def _extract_syntax_features(self, doc) -> Dict[str, float]:
        """Extract syntactic structure features."""
        def get_depth(token):
            depth = 0
            while token.head != token:
                depth += 1
                token = token.head
            return depth
        
        depths = [get_depth(token) for token in doc]
        avg_depth = np.mean(depths) if depths else 0
        
        noun_chunks = list(doc.noun_chunks)
        sentences = list(doc.sents)
        num_sentences = len(sentences) or 1
        
        subordinate_markers = {'because', 'although', 'though', 'while', 'when', 'where',
                              'if', 'unless', 'until', 'since', 'after', 'before', 'that'}
        subordinate_count = sum(1 for token in doc if token.text.lower() in subordinate_markers)
        
        passive_count = sum(1 for token in doc if token.dep_ == 'nsubjpass')
        
        negation_count = sum(1 for token in doc if token.dep_ == 'neg')
        
        return {
            'avg_dependency_depth': float(avg_depth),
            'avg_noun_chunks': len(noun_chunks) / num_sentences,
            'subordinate_clause_ratio': subordinate_count / num_sentences,
            'passive_voice_ratio': passive_count / num_sentences,
            'negation_ratio': negation_count / len(doc) if len(doc) > 0 else 0,
        }
    
    def _extract_sentence_features(self, texts: List[str]) -> Dict[str, float]:
        """Extract sentence-level features."""
        all_text = ' '.join(texts)
        
        question_count = all_text.count('?')
        exclamation_count = all_text.count('!')
        
        if self.nlp:
            doc = self.nlp(all_text)
            sentences = list(doc.sents)
            num_sentences = len(sentences) or 1
            avg_sent_len = np.mean([len(sent) for sent in sentences]) if sentences else 0
        else:
            import re
            sentences = re.split(r'[.!?]+', all_text)
            sentences = [s for s in sentences if s.strip()]
            num_sentences = len(sentences) or 1
            avg_sent_len = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        readability = self._compute_readability(all_text)
        
        return {
            'question_ratio': question_count / num_sentences,
            'exclamation_ratio': exclamation_count / num_sentences,
            'avg_sentence_length': float(avg_sent_len),
            'readability_score': readability,
        }
    
    def _compute_readability(self, text: str) -> float:
        """Compute Flesch-Kincaid readability score."""
        import re
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        syllable_count = sum(self._count_syllables(w) for w in words)
        
        asl = len(words) / len(sentences)
        asw = syllable_count / len(words)
        
        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            count += 1
        
        return max(1, count)
    
    def _extract_basic(self, texts: List[str]) -> Dict[str, float]:
        """Basic extraction without spaCy."""
        return {name: 0.0 for name in self.feature_names}
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
