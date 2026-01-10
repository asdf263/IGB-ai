"""
Linguistic Style Feature Extraction Module
Extracts ~30 linguistic and grammatical features from chat messages
"""
import numpy as np
import re
from typing import List, Dict, Any
from collections import Counter


class LinguisticFeatureExtractor:
    """Extracts linguistic style and grammatical features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'pos_noun_ratio',
            'pos_verb_ratio',
            'pos_adj_ratio',
            'pos_adv_ratio',
            'pos_pronoun_ratio',
            'pos_preposition_ratio',
            'pos_conjunction_ratio',
            'pos_interjection_ratio',
            'first_person_ratio',
            'second_person_ratio',
            'third_person_ratio',
            'past_tense_ratio',
            'present_tense_ratio',
            'future_tense_ratio',
            'modal_verb_ratio',
            'hedge_word_ratio',
            'assertive_word_ratio',
            'intensifier_ratio',
            'negation_ratio',
            'contraction_ratio',
            'filler_word_ratio',
            'formal_word_ratio',
            'informal_word_ratio',
            'avg_clause_depth',
            'subordinate_clause_ratio',
            'interrogative_ratio',
            'declarative_ratio',
            'exclamatory_ratio',
            'imperative_ratio',
            'readability_score'
        ]
        
        self.first_person = {'i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves'}
        self.second_person = {'you', 'your', 'yours', 'yourself', 'yourselves'}
        self.third_person = {'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'}
        
        self.modal_verbs = {'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'}
        self.hedge_words = {'maybe', 'perhaps', 'possibly', 'probably', 'might', 'could', 'seem',
                           'appear', 'suggest', 'think', 'believe', 'guess', 'suppose', 'assume',
                           'somewhat', 'rather', 'quite', 'fairly', 'slightly', 'apparently'}
        self.assertive_words = {'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
                               'undoubtedly', 'surely', 'always', 'never', 'must', 'will', 'know',
                               'certain', 'sure', 'confident', 'guarantee', 'proven', 'fact'}
        self.intensifiers = {'very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally',
                            'completely', 'utterly', 'highly', 'deeply', 'strongly', 'greatly',
                            'seriously', 'literally', 'super', 'so', 'too', 'quite', 'rather'}
        self.negations = {'not', "n't", 'no', 'never', 'none', 'nothing', 'nowhere', 'neither',
                         'nobody', 'hardly', 'scarcely', 'barely', "don't", "doesn't", "didn't",
                         "won't", "wouldn't", "couldn't", "shouldn't", "can't", "isn't", "aren't"}
        self.fillers = {'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean', 'basically',
                       'actually', 'literally', 'honestly', 'well', 'so', 'anyway', 'right'}
        self.formal_words = {'therefore', 'however', 'furthermore', 'moreover', 'nevertheless',
                            'consequently', 'accordingly', 'hence', 'thus', 'whereas', 'whereby',
                            'regarding', 'concerning', 'subsequently', 'previously', 'additionally'}
        self.informal_words = {'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'dunno', 'yeah', 'yep',
                              'nope', 'ok', 'okay', 'cool', 'awesome', 'stuff', 'things', 'guy',
                              'guys', 'dude', 'lol', 'haha', 'omg', 'btw', 'idk', 'tbh', 'imo'}
        
        self.past_indicators = {'was', 'were', 'had', 'did', 'went', 'came', 'saw', 'got', 'made',
                               'said', 'told', 'thought', 'knew', 'took', 'gave', 'found', 'left'}
        self.future_indicators = {'will', 'shall', 'going to', 'gonna', "'ll", 'tomorrow', 'soon',
                                 'later', 'next', 'future', 'eventually', 'someday'}
        
        self.subordinate_markers = {'because', 'although', 'though', 'while', 'when', 'where',
                                   'if', 'unless', 'until', 'since', 'after', 'before', 'that',
                                   'which', 'who', 'whom', 'whose', 'whether', 'whereas'}
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all linguistic features from messages."""
        if not messages:
            return {name: 0.0 for name in self.feature_names}
        
        texts = [msg.get('text', '') for msg in messages if msg.get('text')]
        if not texts:
            return {name: 0.0 for name in self.feature_names}
        
        all_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', all_text)
        total_words = len(words) if words else 1
        
        features = {}
        
        # POS-like ratios (simplified without spaCy)
        pos_features = self._compute_pos_ratios(words)
        features.update(pos_features)
        
        # Pronoun person ratios
        features['first_person_ratio'] = sum(1 for w in words if w in self.first_person) / total_words
        features['second_person_ratio'] = sum(1 for w in words if w in self.second_person) / total_words
        features['third_person_ratio'] = sum(1 for w in words if w in self.third_person) / total_words
        
        # Tense ratios
        features['past_tense_ratio'] = sum(1 for w in words if w in self.past_indicators or w.endswith('ed')) / total_words
        features['present_tense_ratio'] = sum(1 for w in words if w.endswith('ing') or w.endswith('s')) / total_words
        features['future_tense_ratio'] = sum(1 for w in words if w in self.future_indicators) / total_words
        
        # Word category ratios
        features['modal_verb_ratio'] = sum(1 for w in words if w in self.modal_verbs) / total_words
        features['hedge_word_ratio'] = sum(1 for w in words if w in self.hedge_words) / total_words
        features['assertive_word_ratio'] = sum(1 for w in words if w in self.assertive_words) / total_words
        features['intensifier_ratio'] = sum(1 for w in words if w in self.intensifiers) / total_words
        features['negation_ratio'] = sum(1 for w in words if w in self.negations) / total_words
        features['filler_word_ratio'] = sum(1 for w in words if w in self.fillers) / total_words
        features['formal_word_ratio'] = sum(1 for w in words if w in self.formal_words) / total_words
        features['informal_word_ratio'] = sum(1 for w in words if w in self.informal_words) / total_words
        
        # Contraction ratio
        contraction_count = len(re.findall(r"\b\w+'\w+\b", all_text))
        features['contraction_ratio'] = contraction_count / total_words
        
        # Clause features
        features['avg_clause_depth'] = self._estimate_clause_depth(texts)
        features['subordinate_clause_ratio'] = sum(1 for w in words if w in self.subordinate_markers) / total_words
        
        # Sentence type ratios
        sentence_types = self._classify_sentences(texts)
        total_sentences = sum(sentence_types.values()) if sentence_types else 1
        features['interrogative_ratio'] = sentence_types.get('interrogative', 0) / total_sentences
        features['declarative_ratio'] = sentence_types.get('declarative', 0) / total_sentences
        features['exclamatory_ratio'] = sentence_types.get('exclamatory', 0) / total_sentences
        features['imperative_ratio'] = sentence_types.get('imperative', 0) / total_sentences
        
        # Readability score (Flesch-Kincaid approximation)
        features['readability_score'] = self._compute_readability(texts)
        
        return features
    
    def _compute_pos_ratios(self, words: List[str]) -> Dict[str, float]:
        """Compute approximate POS tag ratios using word lists."""
        total = len(words) if words else 1
        
        nouns = {'time', 'year', 'people', 'way', 'day', 'man', 'thing', 'woman', 'life',
                'child', 'world', 'school', 'state', 'family', 'student', 'group', 'country',
                'problem', 'hand', 'part', 'place', 'case', 'week', 'company', 'system'}
        verbs = {'be', 'have', 'do', 'say', 'get', 'make', 'go', 'know', 'take', 'see',
                'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask',
                'work', 'seem', 'feel', 'try', 'leave', 'call', 'need', 'become', 'keep'}
        adjectives = {'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own',
                     'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large',
                     'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same'}
        adverbs = {'up', 'so', 'out', 'just', 'now', 'how', 'then', 'more', 'also', 'here',
                  'well', 'only', 'very', 'even', 'back', 'there', 'down', 'still', 'in',
                  'as', 'too', 'when', 'never', 'really', 'most', 'always', 'often', 'quickly'}
        prepositions = {'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about',
                       'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out',
                       'against', 'during', 'without', 'before', 'under', 'around', 'among'}
        conjunctions = {'and', 'but', 'or', 'so', 'yet', 'for', 'nor', 'because', 'although',
                       'while', 'if', 'when', 'where', 'unless', 'since', 'whether', 'though'}
        interjections = {'oh', 'wow', 'hey', 'hi', 'hello', 'bye', 'yes', 'no', 'yeah',
                        'ok', 'okay', 'please', 'thanks', 'sorry', 'oops', 'uh', 'um', 'ah'}
        
        return {
            'pos_noun_ratio': sum(1 for w in words if w in nouns) / total,
            'pos_verb_ratio': sum(1 for w in words if w in verbs) / total,
            'pos_adj_ratio': sum(1 for w in words if w in adjectives) / total,
            'pos_adv_ratio': sum(1 for w in words if w in adverbs) / total,
            'pos_pronoun_ratio': sum(1 for w in words if w in self.first_person | self.second_person | self.third_person) / total,
            'pos_preposition_ratio': sum(1 for w in words if w in prepositions) / total,
            'pos_conjunction_ratio': sum(1 for w in words if w in conjunctions) / total,
            'pos_interjection_ratio': sum(1 for w in words if w in interjections) / total
        }
    
    def _estimate_clause_depth(self, texts: List[str]) -> float:
        """Estimate average clause depth based on subordinate markers."""
        depths = []
        for text in texts:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                words = sentence.lower().split()
                depth = 1 + sum(1 for w in words if w in self.subordinate_markers)
                depths.append(depth)
        return float(np.mean(depths)) if depths else 1.0
    
    def _classify_sentences(self, texts: List[str]) -> Dict[str, int]:
        """Classify sentences by type."""
        counts = {'interrogative': 0, 'declarative': 0, 'exclamatory': 0, 'imperative': 0}
        
        imperative_starters = {'please', 'do', 'don\'t', 'let', 'go', 'come', 'take', 'give',
                              'make', 'stop', 'start', 'try', 'help', 'tell', 'show', 'wait'}
        
        for text in texts:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                if sentence.endswith('?'):
                    counts['interrogative'] += 1
                elif sentence.endswith('!'):
                    counts['exclamatory'] += 1
                elif sentence.split()[0].lower() in imperative_starters if sentence.split() else False:
                    counts['imperative'] += 1
                else:
                    counts['declarative'] += 1
        
        return counts
    
    def _compute_readability(self, texts: List[str]) -> float:
        """Compute Flesch-Kincaid readability score."""
        all_text = ' '.join(texts)
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', all_text)
        
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
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
