import React, { useCallback, useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useFocusEffect } from '@react-navigation/native';

import { TestCard } from '../components/TestCard';
import { MetricCard } from '../components/MetricCard';
import { NetworkPill } from '../components/NetworkPill';
import { AppButton } from '../components/AppButton';

import { testDefinitions } from '../data/mockData';
import { useNetworkStatus } from '../hooks/useNetworkStatus';
import { colors, spacing, typography } from '../theme';

export function HomeScreen({ navigation }: any) {
  const network = useNetworkStatus();

  const [user, setUser] = useState({
    name: 'Athlete',
    email: '',
    avatarInitials: 'AT',
  });

  useFocusEffect(
    useCallback(() => {
      const loadUser = async () => {
        try {
          const savedUser = await AsyncStorage.getItem('loggedInUser');

          if (savedUser) {
            const parsedUser = JSON.parse(savedUser);

            setUser({
              name: parsedUser.name || 'Athlete',
              email: parsedUser.email || '',
              avatarInitials:
                parsedUser.avatarInitials ||
                (parsedUser.name
                  ? parsedUser.name.substring(0, 2).toUpperCase()
                  : 'AT'),
            });
          }
        } catch (error) {
          console.log('Unable to load user:', error);
        }
      };

      loadUser();
    }, [])
  );

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* HEADER */}
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.eyebrow}>
            SPORTS TALENT AI
          </Text>

          <Text style={styles.greeting}>
            Good evening, {user.name}.
          </Text>

          <Text style={styles.sub}>
            Ready to measure your potential?
          </Text>
        </View>

        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user.avatarInitials}
          </Text>
        </View>
      </View>

      {/* NETWORK */}
      <NetworkPill status={network} />

      {/* HERO */}
      <LinearGradient
        colors={['#1557B7', '#283B96']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.hero}
      >
        <View style={styles.heroGlow} />

        <View style={styles.heroContent}>
          <View style={styles.badge}>
            <Ionicons
              name="sparkles"
              size={13}
              color={colors.white}
            />

            <Text style={styles.badgeText}>
              AI-ASSISTED ASSESSMENT
            </Text>
          </View>

          <Text style={styles.heroTitle}>
            Your next benchmark starts here.
          </Text>

          <Text style={styles.heroText}>
            Complete a guided assessment and keep your
            performance history in one place.
          </Text>

          <AppButton
            title="Start Assessment"
            onPress={() =>
              navigation.navigate('TestSelection')
            }
            style={styles.heroButton}
          />
        </View>
      </LinearGradient>

      {/* PERFORMANCE */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>
          Performance snapshot
        </Text>

        <Text
          onPress={() => navigation.navigate('Performance')}
          style={styles.see}
        >
          View all
        </Text>
      </View>

      <View style={styles.metrics}>
        <MetricCard
          label="Best sit-ups"
          value="32"
          unit="reps"
        />

        <MetricCard
          label="Best jump"
          value="46"
          unit="cm"
          accent={colors.violet}
        />
      </View>

      {/* ASSESSMENTS */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>
          Assessments
        </Text>
      </View>

      {testDefinitions.map((test) => (
        <TestCard
          key={test.id}
          test={test}
          onPress={() =>
            navigation.navigate('Instructions', {
              testType: test.id,
            })
          }
        />
      ))}

      {/* TIP */}
      <View style={styles.tip}>
        <Ionicons
          name="shield-checkmark-outline"
          size={20}
          color={colors.success}
        />

        <View style={styles.tipContent}>
          <Text style={styles.tipTitle}>
            Assessment-ready setup
          </Text>

          <Text style={styles.tipText}>
            Use good lighting, clear floor space and keep
            your full body in frame.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },

  content: {
    padding: spacing.lg,
    paddingTop: 54,
    paddingBottom: 40,
  },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },

  headerText: {
    flex: 1,
    paddingRight: spacing.md,
  },

  eyebrow: {
    ...typography.caption,
    color: colors.primaryBright,
    letterSpacing: 1.5,
  },

  greeting: {
    ...typography.h1,
    color: colors.text,
    marginTop: 4,
  },

  sub: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: 4,
  },

  avatar: {
    width: 48,
    height: 48,
    borderRadius: 17,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },

  avatarText: {
    ...typography.bodyMedium,
    color: colors.primaryBright,
  },

  hero: {
    marginTop: spacing.lg,
    borderRadius: 28,
    padding: spacing.lg,
    overflow: 'hidden',
  },

  heroGlow: {
    position: 'absolute',
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: 'rgba(96,165,250,0.15)',
    right: -55,
    top: -70,
  },

  heroContent: {
    maxWidth: 360,
  },

  badge: {
    alignSelf: 'flex-start',
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.12)',
  },

  badgeText: {
    ...typography.caption,
    color: colors.white,
    letterSpacing: 0.7,
  },

  heroTitle: {
    fontSize: 28,
    lineHeight: 33,
    fontWeight: '800',
    color: colors.white,
    marginTop: 16,
  },

  heroText: {
    ...typography.body,
    color: 'rgba(255,255,255,0.78)',
    marginTop: 9,
  },

  heroButton: {
    backgroundColor: colors.white,
    marginTop: spacing.lg,
  },

  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.xl,
    marginBottom: spacing.md,
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.text,
  },

  see: {
    ...typography.caption,
    color: colors.primaryBright,
  },

  metrics: {
    flexDirection: 'row',
    gap: spacing.md,
  },

  tip: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-start',
    padding: spacing.md,
    borderRadius: 20,
    backgroundColor: 'rgba(34,197,94,0.06)',
    borderWidth: 1,
    borderColor: 'rgba(34,197,94,0.15)',
    marginTop: spacing.sm,
  },

  tipContent: {
    flex: 1,
  },

  tipTitle: {
    ...typography.bodyMedium,
    color: colors.text,
  },

  tipText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 3,
  },
});