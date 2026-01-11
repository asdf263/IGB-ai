import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar, ProgressBar, SegmentedButtons } from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import { AuthContext } from '../../context/AuthContext';
import * as userApi from '../../services/userApi';

const OnboardingStep2_Profile = ({ navigation, route }) => {
  const { updateProfile, user } = useContext(AuthContext);
  const [name, setName] = useState(route.params?.name || user?.profile?.name || '');
  const [instagramHandle, setInstagramHandle] = useState(route.params?.instagramHandle || user?.profile?.instagram_handle || '');
  const [location, setLocation] = useState(route.params?.location || user?.profile?.location || '');
  const [height, setHeight] = useState(route.params?.height || user?.profile?.height || '');
  const [heightUnit, setHeightUnit] = useState(route.params?.heightUnit || user?.profile?.height_unit || 'cm');
  const [ethnicity, setEthnicity] = useState(route.params?.ethnicity || user?.profile?.ethnicity || '');
  const [profilePicture, setProfilePicture] = useState(route.params?.profilePicture || user?.profile?.profile_picture || '');
  const [isLoading, setIsLoading] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const uid = route.params?.uid || user?.uid;

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        setErrorMessage('Permission to access camera roll is required');
        setShowError(true);
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setProfilePicture(base64Image);
      }
    } catch (error) {
      setErrorMessage('Failed to pick image');
      setShowError(true);
    }
  };

  const validateInstagramHandle = (handle) => {
    if (!handle) return true; // Optional field
    const cleaned = handle.replace('@', '');
    return /^[a-zA-Z0-9._]+$/.test(cleaned);
  };

  const handleNext = async () => {
    if (!name.trim()) {
      setErrorMessage('Name is required');
      setShowError(true);
      return;
    }

    if (instagramHandle && !validateInstagramHandle(instagramHandle)) {
      setErrorMessage('Invalid Instagram handle');
      setShowError(true);
      return;
    }

    setIsLoading(true);
    try {
      const profileData = {
        name: name.trim(),
        instagram_handle: instagramHandle.trim().replace(/^@+/, ''),
        profile_picture: profilePicture,
        location: location.trim(),
        height: height.trim(),
        height_unit: heightUnit,
        ethnicity: ethnicity.trim(),
      };

      const result = await updateProfile(profileData);
      
      if (result.success) {
        navigation.navigate('OnboardingStep3', {
          uid,
        });
      } else {
        setErrorMessage(result.error || 'Failed to save profile');
        setShowError(true);
      }
    } catch (error) {
      setErrorMessage(error.message || 'Failed to save profile');
      setShowError(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <ProgressBar progress={0.5} color="#6200ee" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 2 of 4: Your Profile
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Tell us about yourself
          </Text>

          <Button
            mode="outlined"
            onPress={pickImage}
            style={styles.imageButton}
            icon="camera"
          >
            {profilePicture ? 'Change Profile Picture' : 'Add Profile Picture'}
          </Button>

          {profilePicture ? (
            <View style={styles.imagePreview}>
              <Text variant="bodySmall" style={styles.imagePreviewText}>
                Image selected
              </Text>
            </View>
          ) : null}

          <TextInput
            label="Full Name *"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
            disabled={isLoading}
          />

          <TextInput
            label="Instagram Handle"
            value={instagramHandle}
            onChangeText={setInstagramHandle}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            placeholder="@username"
            disabled={isLoading}
          />

          <TextInput
            label="Location"
            value={location}
            onChangeText={setLocation}
            mode="outlined"
            style={styles.input}
            placeholder="City, State, Country"
            disabled={isLoading}
          />

          <View style={styles.heightContainer}>
            <TextInput
              label="Height"
              value={height}
              onChangeText={setHeight}
              mode="outlined"
              style={styles.heightInput}
              keyboardType="numeric"
              disabled={isLoading}
            />
            <SegmentedButtons
              value={heightUnit}
              onValueChange={setHeightUnit}
              buttons={[
                { value: 'cm', label: 'cm' },
                { value: 'in', label: 'in' },
              ]}
              style={styles.unitSelector}
            />
          </View>

          <TextInput
            label="Ethnicity"
            value={ethnicity}
            onChangeText={setEthnicity}
            mode="outlined"
            style={styles.input}
            disabled={isLoading}
          />

          <View style={styles.buttonRow}>
            <Button
              mode="outlined"
              onPress={() => navigation.goBack()}
              style={styles.backButton}
              disabled={isLoading}
            >
              Back
            </Button>
            <Button
              mode="contained"
              onPress={handleNext}
              style={styles.nextButton}
              loading={isLoading}
              disabled={isLoading}
            >
              Continue
            </Button>
          </View>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={3000}
      >
        {errorMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    marginTop: 20,
  },
  progressBar: {
    marginBottom: 24,
    height: 4,
    borderRadius: 2,
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
  imageButton: {
    marginBottom: 16,
  },
  imagePreview: {
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#e3f2fd',
    borderRadius: 4,
  },
  imagePreviewText: {
    color: '#1976d2',
  },
  input: {
    marginBottom: 16,
  },
  heightContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 12,
  },
  heightInput: {
    flex: 1,
  },
  unitSelector: {
    width: 100,
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 8,
    gap: 12,
  },
  backButton: {
    flex: 1,
  },
  nextButton: {
    flex: 1,
  },
});

export default OnboardingStep2_Profile;

