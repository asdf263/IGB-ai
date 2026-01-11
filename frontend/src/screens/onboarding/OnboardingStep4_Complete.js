import React, { useEffect, useContext } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, Text, ProgressBar, Card, Avatar } from 'react-native-paper';
import { AuthContext } from '../../context/AuthContext';
import * as userApi from '../../services/userApi';

const OnboardingStep4_Complete = ({ navigation, route }) => {
  const { user, refreshUser } = useContext(AuthContext);
  const uid = route.params?.uid || user?.uid;

  useEffect(() => {
    // Mark onboarding as complete
    const completeOnboarding = async () => {
      try {
        await userApi.completeOnboarding(uid);
        await refreshUser();
      } catch (error) {
        console.error('Error completing onboarding:', error);
      }
    };

    completeOnboarding();
  }, [uid, refreshUser]);

  const handleGoToDashboard = () => {
    // Navigation will be handled by the navigator
    // The navigator will check onboarding_complete and route accordingly
    navigation.reset({
      index: 0,
      routes: [{ name: 'Main' }],
    });
  };

  const displayName = user?.profile?.name || user?.email || 'User';

  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <View style={styles.content}>
        <ProgressBar progress={1.0} color="#6200ee" style={styles.progressBar} />
        
        <View style={styles.iconContainer}>
          <Avatar.Icon 
            size={80} 
            icon="check-circle" 
            style={styles.successIcon}
          />
        </View>

        <Text variant="headlineSmall" style={styles.title}>
          Welcome, {displayName}!
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Your profile has been set up successfully
        </Text>

        <Card style={styles.profileCard}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.cardTitle}>
              Profile Summary
            </Text>
            
            {user?.profile?.name && (
              <View style={styles.profileRow}>
                <Text variant="bodySmall" style={styles.label}>Name:</Text>
                <Text variant="bodyMedium" style={styles.value}>
                  {user.profile.name}
                </Text>
              </View>
            )}

            {user?.profile?.instagram_handle && (
              <View style={styles.profileRow}>
                <Text variant="bodySmall" style={styles.label}>Instagram:</Text>
                <Text variant="bodyMedium" style={styles.value}>
                  @{user.profile.instagram_handle}
                </Text>
              </View>
            )}

            {user?.profile?.location && (
              <View style={styles.profileRow}>
                <Text variant="bodySmall" style={styles.label}>Location:</Text>
                <Text variant="bodyMedium" style={styles.value}>
                  {user.profile.location}
                </Text>
              </View>
            )}

            {user?.profile?.height && (
              <View style={styles.profileRow}>
                <Text variant="bodySmall" style={styles.label}>Height:</Text>
                <Text variant="bodyMedium" style={styles.value}>
                  {user.profile.height} {user.profile.height_unit || 'cm'}
                </Text>
              </View>
            )}

            {route.params?.vectorId && (
              <View style={styles.profileRow}>
                <Text variant="bodySmall" style={styles.label}>Vector ID:</Text>
                <Text variant="bodyMedium" style={styles.value}>
                  {route.params.vectorId.substring(0, 8)}...
                </Text>
              </View>
            )}
          </Card.Content>
        </Card>

        <Button
          mode="contained"
          onPress={handleGoToDashboard}
          style={styles.button}
          icon="arrow-forward"
        >
          Go to Dashboard
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    marginTop: 40,
  },
  progressBar: {
    marginBottom: 24,
    height: 4,
    borderRadius: 2,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  successIcon: {
    backgroundColor: '#4caf50',
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 32,
    color: '#666',
  },
  profileCard: {
    marginBottom: 32,
  },
  cardTitle: {
    fontWeight: 'bold',
    marginBottom: 16,
  },
  profileRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  label: {
    color: '#666',
    fontWeight: '500',
  },
  value: {
    flex: 1,
    textAlign: 'right',
  },
  button: {
    paddingVertical: 4,
  },
});

export default OnboardingStep4_Complete;

