import React, { useContext, useState, useEffect, useRef } from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity, Dimensions, Animated } from 'react-native';
import { Text, Avatar, Divider, ActivityIndicator } from 'react-native-paper';
import { AuthContext } from '../context/AuthContext';
import { getAllUsers } from '../services/userApi';
import { formatHeightDisplay } from '../constants/profileOptions';

const { width: screenWidth } = Dimensions.get('window');

/**
 * BrowseUsersScreen - Browse through all user profiles with arrow navigation
 */
const BrowseUsersScreen = () => {
  const { user } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Animation values
  const slideAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAllUsers(100, 0);
      // Filter out the current user
      const otherUsers = (response.users || []).filter(u => u.uid !== user?.uid);
      setUsers(otherUsers);
      setCurrentIndex(0);
    } catch (err) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const animateTransition = (direction, callback) => {
    // Animate out
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: direction === 'left' ? -screenWidth * 0.3 : screenWidth * 0.3,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.9,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 0,
        duration: 150,
        useNativeDriver: true,
      }),
    ]).start(() => {
      // Update index
      callback();
      
      // Reset position to opposite side
      slideAnim.setValue(direction === 'left' ? screenWidth * 0.3 : -screenWidth * 0.3);
      
      // Animate in
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          friction: 8,
          tension: 40,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          friction: 8,
          tension: 40,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    });
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      animateTransition('right', () => setCurrentIndex(currentIndex - 1));
    }
  };

  const handleNext = () => {
    if (currentIndex < users.length - 1) {
      animateTransition('left', () => setCurrentIndex(currentIndex + 1));
    }
  };

  const getInitials = (email, name) => {
    if (name) return name.charAt(0).toUpperCase();
    if (!email) return '?';
    return email.charAt(0).toUpperCase();
  };

  const formatHeight = (profileData) => {
    if (!profileData?.height) return 'Not specified';
    return formatHeightDisplay(profileData.height);
  };

  const formatLocation = (profileData) => {
    const city = profileData?.city;
    const country = profileData?.country;
    if (city && country) return `${city}, ${country}`;
    return city || country || profileData?.location || 'Not specified';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6200ee" />
        <Text style={styles.loadingText}>Loading users...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchUsers}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (users.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>👥</Text>
        <Text style={styles.emptyTitle}>No Users Found</Text>
        <Text style={styles.emptySubtitle}>Be the first to invite friends!</Text>
      </View>
    );
  }

  const currentUser = users[currentIndex];
  const profileData = currentUser?.profile || {};
  const displayName = profileData?.name || currentUser?.email?.split('@')[0] || 'User';

  return (
    <View style={styles.container}>
      {/* Main Content Area */}
      <View style={styles.contentArea}>
        {/* Left Arrow */}
        <TouchableOpacity
          style={[styles.arrowButton, styles.leftArrow]}
          onPress={handlePrevious}
          disabled={currentIndex === 0}
          activeOpacity={0.6}
        >
          <Text style={[styles.arrowText, currentIndex === 0 && styles.arrowTextDisabled]}>‹</Text>
        </TouchableOpacity>

        {/* Animated Profile Card */}
        <Animated.View
          style={[
            styles.profileWrapper,
            {
              transform: [
                { translateX: slideAnim },
                { scale: scaleAnim },
              ],
              opacity: opacityAnim,
            },
          ]}
        >
          <ScrollView 
            style={styles.profileScrollView} 
            contentContainerStyle={styles.profileContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Unified Profile Card with 3D effect */}
            <View style={styles.cardContainer}>
              <View style={styles.cardShadowLayer3} />
              <View style={styles.cardShadowLayer2} />
              <View style={styles.cardShadowLayer1} />
              <View style={styles.profileCard}>
                {/* Profile Header */}
                <View style={styles.headerSection}>
                  <View style={styles.avatarContainer}>
                    <Avatar.Text
                      size={110}
                      label={getInitials(currentUser?.email, profileData?.name)}
                      style={styles.avatar}
                      labelStyle={styles.avatarLabel}
                    />
                  </View>
                  <Text style={styles.displayName}>{displayName}</Text>
                  <Text style={styles.email}>{currentUser?.email || 'No email'}</Text>
                  {profileData?.instagram_handle && (
                    <Text style={styles.instagram}>@{profileData.instagram_handle}</Text>
                  )}
                </View>

                {/* Divider */}
                <View style={styles.sectionDivider} />

                {/* Profile Details */}
                <View style={styles.detailsSection}>
                  <Text style={styles.sectionTitle}>Profile Information</Text>
                  <ProfileRow label="Location" value={formatLocation(profileData)} icon="📍" />
                  <ProfileRow label="Ethnicity" value={profileData?.ethnicity || 'Not specified'} icon="🌍" />
                  <ProfileRow label="Height" value={formatHeight(profileData)} icon="📏" />
                  <ProfileRow label="Age" value={profileData?.age ? `${profileData.age} years` : 'Not specified'} icon="🎂" />
                </View>
              </View>
            </View>
          </ScrollView>
        </Animated.View>

        {/* Right Arrow */}
        <TouchableOpacity
          style={[styles.arrowButton, styles.rightArrow]}
          onPress={handleNext}
          disabled={currentIndex === users.length - 1}
          activeOpacity={0.6}
        >
          <Text style={[styles.arrowText, currentIndex === users.length - 1 && styles.arrowTextDisabled]}>›</Text>
        </TouchableOpacity>
      </View>

      {/* User Index Indicator */}
      <View style={styles.indexIndicator}>
        <View style={styles.dotsContainer}>
          {users.length <= 10 ? (
            users.map((_, index) => (
              <View
                key={index}
                style={[
                  styles.dot,
                  index === currentIndex && styles.dotActive,
                ]}
              />
            ))
          ) : (
            <Text style={styles.indexText}>
              {currentIndex + 1} of {users.length}
            </Text>
          )}
        </View>
      </View>
    </View>
  );
};

// Helper component for profile rows
const ProfileRow = ({ label, value, icon }) => (
  <View style={styles.profileRow}>
    <View style={styles.rowLeft}>
      <Text style={styles.rowIcon}>{icon}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
    <Text style={styles.value}>{value}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f2f5',
  },
  loadingText: {
    marginTop: 12,
    color: '#666',
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f0f2f5',
  },
  errorText: {
    color: '#d32f2f',
    marginBottom: 16,
    textAlign: 'center',
    fontSize: 16,
  },
  retryButton: {
    backgroundColor: '#6200ee',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f0f2f5',
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#666',
  },
  contentArea: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  // Minimal arrow buttons
  arrowButton: {
    width: 44,
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  leftArrow: {
    paddingLeft: 4,
  },
  rightArrow: {
    paddingRight: 4,
  },
  arrowText: {
    fontSize: 56,
    color: '#6200ee',
    fontWeight: '300',
    textShadowColor: 'rgba(98, 0, 238, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  arrowTextDisabled: {
    color: '#ccc',
    textShadowColor: 'transparent',
  },
  profileWrapper: {
    flex: 1,
    height: '100%',
  },
  profileScrollView: {
    flex: 1,
  },
  profileContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 8,
    paddingVertical: 16,
  },
  // 3D Card Container
  cardContainer: {
    position: 'relative',
    marginHorizontal: 4,
  },
  cardShadowLayer3: {
    position: 'absolute',
    top: 12,
    left: 8,
    right: 8,
    bottom: -12,
    backgroundColor: 'rgba(98, 0, 238, 0.08)',
    borderRadius: 24,
  },
  cardShadowLayer2: {
    position: 'absolute',
    top: 8,
    left: 5,
    right: 5,
    bottom: -8,
    backgroundColor: 'rgba(98, 0, 238, 0.12)',
    borderRadius: 22,
  },
  cardShadowLayer1: {
    position: 'absolute',
    top: 4,
    left: 2,
    right: 2,
    bottom: -4,
    backgroundColor: 'rgba(98, 0, 238, 0.18)',
    borderRadius: 20,
  },
  profileCard: {
    backgroundColor: '#fff',
    borderRadius: 20,
    overflow: 'hidden',
    // iOS shadow
    shadowColor: '#6200ee',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    // Android shadow
    elevation: 12,
  },
  // Header Section
  headerSection: {
    alignItems: 'center',
    paddingTop: 32,
    paddingBottom: 24,
    paddingHorizontal: 20,
    backgroundColor: '#fafafa',
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: {
    backgroundColor: '#6200ee',
  },
  avatarLabel: {
    fontSize: 44,
    fontWeight: '600',
  },
  displayName: {
    fontSize: 26,
    fontWeight: '700',
    color: '#1a1a2e',
    marginBottom: 4,
  },
  email: {
    fontSize: 15,
    color: '#666',
    marginBottom: 4,
  },
  instagram: {
    fontSize: 14,
    color: '#6200ee',
    fontWeight: '500',
  },
  sectionDivider: {
    height: 1,
    backgroundColor: '#e8e8e8',
    marginHorizontal: 20,
  },
  // Details Section
  detailsSection: {
    padding: 20,
    paddingTop: 16,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#999',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 16,
  },
  profileRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rowIcon: {
    fontSize: 18,
    marginRight: 12,
  },
  label: {
    fontSize: 15,
    color: '#666',
  },
  value: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1a1a2e',
  },
  // Index Indicator
  indexIndicator: {
    paddingVertical: 16,
    alignItems: 'center',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e8e8e8',
  },
  dotsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ddd',
    marginHorizontal: 4,
  },
  dotActive: {
    backgroundColor: '#6200ee',
    width: 24,
  },
  indexText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '500',
  },
});

export default BrowseUsersScreen;
