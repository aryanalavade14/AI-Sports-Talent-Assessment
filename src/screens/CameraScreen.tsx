
import React, { useState } from 'react';
import {
  Alert,
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography } from '../theme';

export function CameraScreen({ navigation, route }: any) {
  const { testType } = route.params;
  const [picking, setPicking] = useState(false);

  const isSitup = testType === 'situp';

  async function chooseVideo() {
    try {
      setPicking(true);

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['videos'],
        allowsEditing: false,
        quality: 1,
      });

      if (result.canceled) {
        return;
      }

      const video = result.assets?.[0];

      if (!video?.uri) {
        Alert.alert(
          'Video not found',
          'Please select a valid video and try again.'
        );
        return;
      }

      navigation.replace('Preview', {
        testType,
        videoUri: video.uri,
      });
    } catch (error) {
      console.log('Video selection error:', error);

      Alert.alert(
        'Unable to select video',
        'Please try choosing a video from your gallery again.'
      );
    } finally {
      setPicking(false);
    }
  }

  return (
    <SafeAreaView
      style={styles.screen}
      edges={['top', 'left', 'right']}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
            accessibilityLabel="Go back"
            activeOpacity={0.7}
          >
            <Ionicons
              name="arrow-back"
              size={23}
              color={colors.text}
            />
          </TouchableOpacity>

          <Text style={styles.headerTitle}>Upload Video</Text>

          <View style={styles.headerSpacer} />
        </View>

        {/* Test type */}
        <View style={styles.testPill}>
          <Ionicons
            name={isSitup ? 'fitness-outline' : 'flash-outline'}
            size={17}
            color={colors.primaryBright}
          />

          <Text style={styles.testText}>
            {isSitup
              ? 'SIT-UPS ASSESSMENT'
              : 'VERTICAL JUMP ASSESSMENT'}
          </Text>
        </View>

        {/* Main upload section */}
        <View style={styles.hero}>
          <View style={styles.iconCircle}>
            <Ionicons
              name="cloud-upload-outline"
              size={58}
              color={colors.primaryBright}
            />
          </View>

          <Text style={styles.title}>
            Choose Your Video
          </Text>

          <Text style={styles.subtitle}>
            Upload a video of your{' '}
            {isSitup ? 'sit-up exercise' : 'vertical jump'} from
            your phone gallery to begin your assessment.
          </Text>

          {/* Upload card */}
          <View style={styles.uploadCard}>
            <View style={styles.videoIconCircle}>
              <Ionicons
                name="videocam-outline"
                size={30}
                color={colors.cyan}
              />
            </View>

            <Text style={styles.cardTitle}>
              Select a video from your gallery
            </Text>

            <Text style={styles.cardDescription}>
              Choose a clear video where your full body and
              movements are visible.
            </Text>

            {/* Video tips */}
            <View style={styles.tipRow}>
              <Ionicons
                name="checkmark-circle"
                size={19}
                color={colors.cyan}
              />
              <Text style={styles.tipText}>
                Keep your full body in the frame
              </Text>
            </View>

            <View style={styles.tipRow}>
              <Ionicons
                name="checkmark-circle"
                size={19}
                color={colors.cyan}
              />
              <Text style={styles.tipText}>
                Use a well-lit recording
              </Text>
            </View>

            <View style={styles.tipRow}>
              <Ionicons
                name="checkmark-circle"
                size={19}
                color={colors.cyan}
              />
              <Text style={styles.tipText}>
                Avoid shaky or obstructed videos
              </Text>
            </View>

            {/* Gallery button */}
            <TouchableOpacity
              style={[
                styles.uploadButton,
                picking && styles.disabledButton,
              ]}
              onPress={chooseVideo}
              disabled={picking}
              activeOpacity={0.8}
            >
              {picking ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <>
                  <Ionicons
                    name="images-outline"
                    size={22}
                    color="#FFFFFF"
                  />

                  <Text style={styles.uploadButtonText}>
                    Choose from Gallery
                  </Text>
                </>
              )}
            </TouchableOpacity>

            <Text style={styles.privacyText}>
              Select a video stored on your device.
            </Text>
          </View>
        </View>

        {/* Bottom note */}
        <View style={styles.footer}>
          <Ionicons
            name="information-circle-outline"
            size={20}
            color={colors.textSecondary}
          />

          <Text style={styles.footerText}>
            You can review your selected video before continuing.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },

  content: {
    flexGrow: 1,
    paddingHorizontal: 22,
    paddingTop: 14,
    paddingBottom: 28,
  },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 28,
  },

  backButton: {
    width: 44,
    height: 44,
    borderRadius: 15,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
  },

  headerTitle: {
    ...typography.h1,
    color: colors.text,
    fontSize: 20,
  },

  headerSpacer: {
    width: 44,
  },

  testPill: {
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: 'rgba(59,130,246,0.12)',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 30,
    marginBottom: 25,
  },

  testText: {
    ...typography.caption,
    color: colors.primaryBright,
    fontWeight: '800',
    letterSpacing: 0.8,
  },

  hero: {
    alignItems: 'center',
  },

  iconCircle: {
    width: 112,
    height: 112,
    borderRadius: 36,
    backgroundColor: 'rgba(59,130,246,0.14)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 22,
  },

  title: {
    ...typography.h1,
    color: '#F8FAFC',
    textAlign: 'center',
    fontSize: 27,
    marginBottom: 12,
  },

  subtitle: {
    ...typography.body,
    color: '#B8C5D9',
    textAlign: 'center',
    lineHeight: 23,
    paddingHorizontal: 8,
    marginBottom: 28,
  },

  uploadCard: {
    width: '100%',
    backgroundColor: '#FFFFFF',
    borderRadius: 26,
    paddingHorizontal: 22,
    paddingTop: 24,
    paddingBottom: 22,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },

  videoIconCircle: {
    width: 62,
    height: 62,
    borderRadius: 21,
    backgroundColor: '#E0F7FA',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
  },

  cardTitle: {
    ...typography.bodyMedium,
    color: '#172033',
    fontSize: 17,
    textAlign: 'center',
    marginBottom: 10,
  },

  cardDescription: {
    ...typography.body,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 22,
  },

  tipRow: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'stretch',
    marginBottom: 14,
    gap: 10,
  },

  tipText: {
    ...typography.body,
    color: '#334155',
    flex: 1,
    lineHeight: 21,
  },

  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'stretch',
    backgroundColor: '#347FF0',
    paddingVertical: 18,
    paddingHorizontal: 16,
    borderRadius: 16,
    marginTop: 14,
    gap: 10,
  },

  disabledButton: {
    opacity: 0.65,
  },

  uploadButtonText: {
    ...typography.bodyMedium,
    color: '#FFFFFF',
    fontSize: 16,
  },

  privacyText: {
    ...typography.caption,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 15,
  },

  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 24,
    paddingHorizontal: 8,
  },

  footerText: {
    ...typography.caption,
    color: '#B8C5D9',
    flex: 1,
    lineHeight: 19,
  },
});
