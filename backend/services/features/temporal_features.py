"""
Temporal Feature Extraction Module
Extracts ~20 temporal dynamics features from chat messages
"""
import numpy as np
from typing import List, Dict, Any
from datetime import datetime


class TemporalFeatureExtractor:
    """Extracts temporal pattern features from chat messages."""
    
    def __init__(self):
        self.feature_names = [
            'avg_response_latency',
            'median_response_latency',
            'std_response_latency',
            'min_response_latency',
            'max_response_latency',
            'response_latency_skewness',
            'response_latency_kurtosis',
            'burstiness_score',
            'message_interval_autocorr',
            'avg_messages_per_hour',
            'avg_messages_per_day',
            'message_frequency_variance',
            'session_count',
            'avg_session_length',
            'circadian_morning_ratio',
            'circadian_afternoon_ratio',
            'circadian_evening_ratio',
            'circadian_night_ratio',
            'weekday_ratio',
            'weekend_ratio'
        ]
    
    def extract(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract all temporal features from messages."""
        if not messages or len(messages) < 2:
            return {name: 0.0 for name in self.feature_names}
        
        timestamps = self._extract_timestamps(messages)
        intervals = self._compute_intervals(timestamps)
        response_latencies = self._compute_response_latencies(messages)
        
        features = {}
        
        # Response latency statistics
        if response_latencies:
            features['avg_response_latency'] = float(np.mean(response_latencies))
            features['median_response_latency'] = float(np.median(response_latencies))
            features['std_response_latency'] = float(np.std(response_latencies))
            features['min_response_latency'] = float(np.min(response_latencies))
            features['max_response_latency'] = float(np.max(response_latencies))
            features['response_latency_skewness'] = self._compute_skewness(response_latencies)
            features['response_latency_kurtosis'] = self._compute_kurtosis(response_latencies)
        else:
            for key in ['avg_response_latency', 'median_response_latency', 'std_response_latency',
                       'min_response_latency', 'max_response_latency', 'response_latency_skewness',
                       'response_latency_kurtosis']:
                features[key] = 0.0
        
        # Burstiness and autocorrelation
        features['burstiness_score'] = self._compute_burstiness(intervals)
        features['message_interval_autocorr'] = self._compute_autocorrelation(intervals)
        
        # Message frequency
        freq_features = self._compute_frequency_features(timestamps)
        features.update(freq_features)
        
        # Session features
        session_features = self._compute_session_features(timestamps)
        features.update(session_features)
        
        # Circadian features
        circadian_features = self._compute_circadian_features(timestamps)
        features.update(circadian_features)
        
        # Day of week features
        dow_features = self._compute_day_of_week_features(timestamps)
        features.update(dow_features)
        
        return features
    
    def _extract_timestamps(self, messages: List[Dict[str, Any]]) -> List[float]:
        """Extract timestamps from messages."""
        timestamps = []
        for msg in messages:
            ts = msg.get('timestamp', 0)
            if isinstance(ts, (int, float)):
                timestamps.append(float(ts))
            elif isinstance(ts, str):
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt.timestamp())
                except:
                    timestamps.append(0.0)
        return sorted(timestamps)
    
    def _compute_intervals(self, timestamps: List[float]) -> List[float]:
        """Compute time intervals between consecutive messages."""
        if len(timestamps) < 2:
            return []
        return [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    
    def _compute_response_latencies(self, messages: List[Dict[str, Any]]) -> List[float]:
        """Compute response latencies for user messages following bot messages."""
        latencies = []
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            if prev_msg.get('sender') != curr_msg.get('sender'):
                prev_ts = prev_msg.get('timestamp', 0)
                curr_ts = curr_msg.get('timestamp', 0)
                if prev_ts and curr_ts:
                    latency = abs(float(curr_ts) - float(prev_ts))
                    if latency > 0:
                        latencies.append(latency)
        return latencies
    
    def _compute_skewness(self, data: List[float]) -> float:
        """Compute skewness of data."""
        if len(data) < 3:
            return 0.0
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return float(np.mean(((arr - mean) / std) ** 3))
    
    def _compute_kurtosis(self, data: List[float]) -> float:
        """Compute kurtosis of data."""
        if len(data) < 4:
            return 0.0
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return float(np.mean(((arr - mean) / std) ** 4) - 3)
    
    def _compute_burstiness(self, intervals: List[float]) -> float:
        """Compute burstiness score (coefficient of variation)."""
        if not intervals:
            return 0.0
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        if mean_interval == 0:
            return 0.0
        return float((std_interval - mean_interval) / (std_interval + mean_interval))
    
    def _compute_autocorrelation(self, intervals: List[float], lag: int = 1) -> float:
        """Compute autocorrelation of intervals."""
        if len(intervals) <= lag:
            return 0.0
        arr = np.array(intervals)
        mean = np.mean(arr)
        var = np.var(arr)
        if var == 0:
            return 0.0
        autocorr = np.correlate(arr - mean, arr - mean, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        return float(autocorr[lag] / autocorr[0]) if autocorr[0] != 0 else 0.0
    
    def _compute_frequency_features(self, timestamps: List[float]) -> Dict[str, float]:
        """Compute message frequency features."""
        if len(timestamps) < 2:
            return {
                'avg_messages_per_hour': 0.0,
                'avg_messages_per_day': 0.0,
                'message_frequency_variance': 0.0
            }
        
        total_duration = timestamps[-1] - timestamps[0]
        if total_duration <= 0:
            return {
                'avg_messages_per_hour': 0.0,
                'avg_messages_per_day': 0.0,
                'message_frequency_variance': 0.0
            }
        
        hours = total_duration / 3600
        days = total_duration / 86400
        
        msg_per_hour = len(timestamps) / max(hours, 1)
        msg_per_day = len(timestamps) / max(days, 1)
        
        # Compute hourly message counts for variance
        hourly_counts = {}
        for ts in timestamps:
            hour_key = int(ts // 3600)
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
        
        variance = float(np.var(list(hourly_counts.values()))) if hourly_counts else 0.0
        
        return {
            'avg_messages_per_hour': float(msg_per_hour),
            'avg_messages_per_day': float(msg_per_day),
            'message_frequency_variance': variance
        }
    
    def _compute_session_features(self, timestamps: List[float], 
                                   session_gap: float = 1800) -> Dict[str, float]:
        """Compute session-based features (session = gap > 30 min)."""
        if len(timestamps) < 2:
            return {'session_count': 1.0, 'avg_session_length': 0.0}
        
        sessions = []
        session_start = timestamps[0]
        session_end = timestamps[0]
        
        for i in range(1, len(timestamps)):
            if timestamps[i] - timestamps[i-1] > session_gap:
                sessions.append(session_end - session_start)
                session_start = timestamps[i]
            session_end = timestamps[i]
        
        sessions.append(session_end - session_start)
        
        return {
            'session_count': float(len(sessions)),
            'avg_session_length': float(np.mean(sessions)) if sessions else 0.0
        }
    
    def _compute_circadian_features(self, timestamps: List[float]) -> Dict[str, float]:
        """Compute circadian rhythm features."""
        if not timestamps:
            return {
                'circadian_morning_ratio': 0.25,
                'circadian_afternoon_ratio': 0.25,
                'circadian_evening_ratio': 0.25,
                'circadian_night_ratio': 0.25
            }
        
        morning = afternoon = evening = night = 0
        
        for ts in timestamps:
            try:
                dt = datetime.fromtimestamp(ts)
                hour = dt.hour
                if 6 <= hour < 12:
                    morning += 1
                elif 12 <= hour < 18:
                    afternoon += 1
                elif 18 <= hour < 22:
                    evening += 1
                else:
                    night += 1
            except:
                continue
        
        total = morning + afternoon + evening + night
        if total == 0:
            total = 1
        
        return {
            'circadian_morning_ratio': morning / total,
            'circadian_afternoon_ratio': afternoon / total,
            'circadian_evening_ratio': evening / total,
            'circadian_night_ratio': night / total
        }
    
    def _compute_day_of_week_features(self, timestamps: List[float]) -> Dict[str, float]:
        """Compute day of week features."""
        if not timestamps:
            return {'weekday_ratio': 0.5, 'weekend_ratio': 0.5}
        
        weekday = weekend = 0
        
        for ts in timestamps:
            try:
                dt = datetime.fromtimestamp(ts)
                if dt.weekday() < 5:
                    weekday += 1
                else:
                    weekend += 1
            except:
                continue
        
        total = weekday + weekend
        if total == 0:
            total = 1
        
        return {
            'weekday_ratio': weekday / total,
            'weekend_ratio': weekend / total
        }
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()
