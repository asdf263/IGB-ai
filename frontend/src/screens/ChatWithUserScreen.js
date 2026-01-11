import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  TouchableOpacity,
  Keyboard,
} from 'react-native';
import { Text, Avatar, ActivityIndicator } from 'react-native-paper';
import { chatWithUser } from '../services/userApi';

/**
 * ChatWithUserScreen - Chat with an AI persona simulating another user
 * The AI is trained on the target user's communication patterns
 */
const ChatWithUserScreen = ({ route, navigation }) => {
  const { targetUid, targetName, targetUser } = route.params || {};
  
  const [messages, setMessages] = useState([
    {
      role: 'system',
      content: `You're now chatting with an AI that simulates ${targetName}'s communication style. This AI has learned from their chat patterns to mimic how they text.`,
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const scrollViewRef = useRef(null);
  
  useEffect(() => {
    // Set navigation title
    navigation.setOptions({
      title: `Chat with ${targetName}`,
    });
  }, [navigation, targetName]);
  
  const scrollToBottom = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };
  
  const handleSend = async () => {
    if (!inputText.trim() || loading) return;
    
    const userMessage = inputText.trim();
    setInputText('');
    Keyboard.dismiss();
    setError(null);
    
    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    scrollToBottom();
    
    setLoading(true);
    
    try {
      // Build conversation history for context (exclude system messages)
      const history = newMessages
        .filter(m => m.role !== 'system')
        .map(m => ({ role: m.role, content: m.content }));
      
      const result = await chatWithUser(targetUid, userMessage, history);
      
      if (result.success) {
        setMessages([...newMessages, { role: 'assistant', content: result.response }]);
        scrollToBottom();
      } else {
        setError('Failed to get response');
      }
    } catch (err) {
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };
  
  const getInitials = (name) => {
    if (!name) return '?';
    return name.charAt(0).toUpperCase();
  };
  
  const renderMessage = (message, index) => {
    if (message.role === 'system') {
      return (
        <View key={index} style={styles.systemMessageContainer}>
          <Text style={styles.systemMessageText}>{message.content}</Text>
        </View>
      );
    }
    
    const isUser = message.role === 'user';
    
    return (
      <View
        key={index}
        style={[
          styles.messageRow,
          isUser ? styles.messageRowUser : styles.messageRowAssistant,
        ]}
      >
        {!isUser && (
          <Avatar.Text
            size={32}
            label={getInitials(targetName)}
            style={styles.avatar}
            labelStyle={styles.avatarLabel}
          />
        )}
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.messageBubbleUser : styles.messageBubbleAssistant,
          ]}
        >
          <Text
            style={[
              styles.messageText,
              isUser ? styles.messageTextUser : styles.messageTextAssistant,
            ]}
          >
            {message.content}
          </Text>
        </View>
        {isUser && (
          <Avatar.Text
            size={32}
            label="You"
            style={styles.avatarUser}
            labelStyle={styles.avatarLabelUser}
          />
        )}
      </View>
    );
  };
  
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      {/* Chat Header */}
      <View style={styles.header}>
        <Avatar.Text
          size={40}
          label={getInitials(targetName)}
          style={styles.headerAvatar}
          labelStyle={styles.headerAvatarLabel}
        />
        <View style={styles.headerInfo}>
          <Text style={styles.headerName}>{targetName}'s AI</Text>
          <Text style={styles.headerSubtitle}>Simulated conversation</Text>
        </View>
      </View>
      
      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={scrollToBottom}
      >
        {messages.map(renderMessage)}
        
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#E07A5F" />
            <Text style={styles.loadingText}>Thinking...</Text>
          </View>
        )}
        
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}
      </ScrollView>
      
      {/* Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder={`Message ${targetName}...`}
          placeholderTextColor="#999"
          multiline
          maxLength={1000}
          returnKeyType="send"
          onSubmitEditing={handleSend}
          blurOnSubmit={false}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!inputText.trim() || loading) && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e8e8e8',
  },
  headerAvatar: {
    backgroundColor: '#E07A5F',
  },
  headerAvatarLabel: {
    fontSize: 16,
    fontWeight: '600',
  },
  headerInfo: {
    marginLeft: 12,
  },
  headerName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a2e',
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#666',
    marginTop: 2,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 24,
  },
  systemMessageContainer: {
    backgroundColor: '#e8e8e8',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    alignSelf: 'center',
    maxWidth: '90%',
  },
  systemMessageText: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    lineHeight: 18,
  },
  messageRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  messageRowUser: {
    justifyContent: 'flex-end',
  },
  messageRowAssistant: {
    justifyContent: 'flex-start',
  },
  avatar: {
    backgroundColor: '#E07A5F',
    marginRight: 8,
  },
  avatarLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  avatarUser: {
    backgroundColor: '#4caf50',
    marginLeft: 8,
  },
  avatarLabelUser: {
    fontSize: 10,
    fontWeight: '600',
  },
  messageBubble: {
    maxWidth: '70%',
    borderRadius: 16,
    padding: 12,
    paddingHorizontal: 16,
  },
  messageBubbleUser: {
    backgroundColor: '#E07A5F',
    borderBottomRightRadius: 4,
  },
  messageBubbleAssistant: {
    backgroundColor: '#fff',
    borderBottomLeftRadius: 4,
    // Shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 21,
  },
  messageTextUser: {
    color: '#fff',
  },
  messageTextAssistant: {
    color: '#1a1a2e',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
  },
  loadingText: {
    marginLeft: 8,
    color: '#666',
    fontSize: 14,
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
    textAlign: 'center',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e8e8e8',
  },
  input: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    paddingTop: 10,
    fontSize: 15,
    maxHeight: 100,
    color: '#1a1a2e',
  },
  sendButton: {
    backgroundColor: '#E07A5F',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    marginLeft: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
});

export default ChatWithUserScreen;

