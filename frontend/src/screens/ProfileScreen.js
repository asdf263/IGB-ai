import React, { useContext, useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, Avatar, Divider, ActivityIndicator, Chip } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { AuthContext } from '../context/AuthContext';
import { getUser } from '../services/userApi';
import { formatHeightDisplay } from '../constants/profileOptions';

/**
 * ProfileScreen - Displays user profile information
 * 
 * @param {Object} props
 * @param {string} props.userId - Optional user ID to view another user's profile
 *                                If not provided, shows the current authenticated user's profile
 */
const ProfileScreen = ({ route }) => {
  const { user, logout } = useContext(AuthContext);
  const navigation = useNavigation();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [vectorId, setVectorId] = useState(null);

  // Check if viewing another user's profile
  const viewingUserId = route?.params?.userId;
  const isOwnProfile = !viewingUserId || viewingUserId === user?.uid;

  useEffect(() => {
    if (isOwnProfile) {
      // Use cached user data from AuthContext
      setProfileData({
        email: user?.email,
        ...user?.profile,
      });
      // Fetch vector status for own profile
      if (user?.uid) {
        fetchVectorStatus(user.uid);
      }
    } else {
      // Fetch other user's profile
      fetchUserProfile(viewingUserId);
    }
  }, [viewingUserId, user, isOwnProfile]);

  const fetchVectorStatus = async (uid) => {
    try {
      const userData = await getUser(uid);
      setVectorId(userData?.vector_id || null);
    } catch (err) {
      console.log('[PROFILE] Could not fetch vector status:', err.message);
    }
  };

  const fetchUserProfile = async (uid) => {
    setLoading(true);
    setError(null);
    try {
      const userData = await getUser(uid);
      setProfileData({
        email: userData.email,
        ...userData.profile,
      });
    } catch (err) {
      setError(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: () => logout(),
        },
      ]
    );
  };

  const getInitials = (email) => {
    if (!email) return '?';
    return email.charAt(0).toUpperCase();
  };

  const formatHeight = () => {
    if (!profileData?.height) return 'Not specified';
    return formatHeightDisplay(profileData.height);
  };

  const formatLocation = () => {
    const city = profileData?.city;
    const state = profileData?.state;
    if (city && state) return `${city}, ${state}`;
    return city || state || profileData?.location || 'Not specified';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#E07A5F" />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Button mode="contained" onPress={() => fetchUserProfile(viewingUserId)}>
          Retry
        </Button>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <Card style={styles.headerCard}>
        <View style={styles.headerContent}>
          <Avatar.Text
            size={80}
            label={getInitials(profileData?.email)}
            style={styles.avatar}
          />
          <Text style={styles.email}>{profileData?.email || 'No email'}</Text>
          {isOwnProfile && (
            <Text style={styles.ownProfileBadge}>Your Profile</Text>
          )}
        </View>
      </Card>

      {/* Profile Details */}
      <Card style={styles.card}>
        <Card.Title title="Profile Information" />
        <Card.Content>
          <ProfileRow label="Location" value={formatLocation()} />
          <Divider style={styles.divider} />
          <ProfileRow label="Ethnicity" value={profileData?.ethnicity || 'Not specified'} />
          <Divider style={styles.divider} />
          <ProfileRow label="Height" value={formatHeight()} />
          <Divider style={styles.divider} />
          <ProfileRow label="Age" value={profileData?.age ? `${profileData.age} years` : 'Not specified'} />
        </Card.Content>
      </Card>

      {/* Chat Data Management - Only show for own profile */}
      {isOwnProfile && (
        <Card style={styles.card}>
          <Card.Title title="Chat Data" />
          <Card.Content>
            <View style={styles.chatDataRow}>
              <View style={styles.chatDataStatus}>
                {vectorId ? (
                  <>
                    <Chip icon="check-circle" style={styles.successChip}>Uploaded</Chip>
                    <Text variant="bodySmall" style={styles.vectorIdText}>
                      ID: {vectorId.slice(0, 15)}...
                    </Text>
                  </>
                ) : (
                  <Chip icon="alert-circle" style={styles.warningChip}>Not Uploaded</Chip>
                )}
              </View>
            </View>
            <Button
              mode="contained"
              onPress={() => navigation.navigate('ChatDataUpload')}
              icon="cloud-upload"
              style={styles.uploadButton}
            >
              {vectorId ? 'Update Chat Data' : 'Upload Chat Data'}
            </Button>
            <Text variant="bodySmall" style={styles.uploadHint}>
              Upload your Instagram data to enable compatibility matching
            </Text>
          </Card.Content>
        </Card>
      )}

      {/* Account Actions - Only show for own profile */}
      {isOwnProfile && (
        <Card style={styles.card}>
          <Card.Title title="Account" />
          <Card.Content>
            <Button
              mode="outlined"
              onPress={handleLogout}
              icon="logout"
              textColor="#d32f2f"
              style={styles.logoutButton}
            >
              Sign Out
            </Button>
          </Card.Content>
        </Card>
      )}

      {/* User Stats - Placeholder for future features */}
      <Card style={styles.card}>
        <Card.Title title="Activity" />
        <Card.Content>
          <View style={styles.statsRow}>
            <StatBox label="Vectors" value="-" />
            <StatBox label="Matches" value="-" />
            <StatBox label="Chats" value="-" />
          </View>
          <Text style={styles.comingSoon}>More stats coming soon</Text>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

// Helper component for profile rows
const ProfileRow = ({ label, value }) => (
  <View style={styles.profileRow}>
    <Text style={styles.label}>{label}</Text>
    <Text style={styles.value}>{value}</Text>
  </View>
);

// Helper component for stats
const StatBox = ({ label, value }) => (
  <View style={styles.statBox}>
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 12,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  errorText: {
    color: '#d32f2f',
    marginBottom: 16,
    textAlign: 'center',
  },
  headerCard: {
    margin: 10,
    marginBottom: 5,
    elevation: 4,
  },
  headerContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatar: {
    backgroundColor: '#E07A5F',
    marginBottom: 12,
  },
  email: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  ownProfileBadge: {
    marginTop: 8,
    fontSize: 12,
    color: '#E07A5F',
    backgroundColor: '#FFEEE8',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    overflow: 'hidden',
  },
  card: {
    margin: 10,
    marginTop: 5,
    elevation: 4,
  },
  profileRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  label: {
    fontSize: 14,
    color: '#666',
  },
  value: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  divider: {
    backgroundColor: '#e0e0e0',
  },
  logoutButton: {
    borderColor: '#d32f2f',
    marginTop: 8,
  },
  chatDataRow: {
    marginBottom: 12,
  },
  chatDataStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  successChip: {
    backgroundColor: '#e8f5e9',
  },
  warningChip: {
    backgroundColor: '#fff3e0',
  },
  vectorIdText: {
    color: '#666',
    fontSize: 11,
  },
  uploadButton: {
    backgroundColor: '#E07A5F',
    marginBottom: 8,
  },
  uploadHint: {
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 12,
  },
  statBox: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E07A5F',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  comingSoon: {
    textAlign: 'center',
    fontSize: 12,
    color: '#999',
    marginTop: 8,
    fontStyle: 'italic',
  },
});

export default ProfileScreen;

