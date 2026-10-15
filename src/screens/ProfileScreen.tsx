import React, { useCallback, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';

import { AppCard } from '../components/AppCard';
import { colors, spacing, typography } from '../theme';

export function ProfileScreen({ navigation }: any) {
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
          console.log('Unable to load profile:', error);
        }
      };

      loadUser();
    }, [])
  );

  return (
    <View style={styles.screen}>
      <Text style={styles.eyebrow}>ATHLETE PROFILE</Text>

      <Text style={styles.title}>Your profile</Text>

      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user.avatarInitials}
          </Text>
        </View>

        <View style={styles.userInfo}>
          <Text style={styles.profileName}>
            {user.name}
          </Text>

          <Text style={styles.email}>
            {user.email}
          </Text>

          <View style={styles.sport}>
            <Ionicons
              name="fitness-outline"
              size={14}
              color={colors.primaryBright}
            />

            <Text style={styles.sportText}>
              Multi-sport
            </Text>
          </View>
        </View>
      </View>

      <AppCard
        title="Performance"
        subtitle="See your assessment trends"
        icon={
          <Ionicons
            name="analytics-outline"
            size={23}
            color={colors.primaryBright}
          />
        }
        onPress={() => navigation.navigate('Performance')}
        style={styles.card}
      />

      <AppCard
        title="Settings"
        subtitle="Preferences and app information"
        icon={
          <Ionicons
            name="settings-outline"
            size={23}
            color={colors.textSecondary}
          />
        }
        onPress={() => navigation.navigate('Settings')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.lg,
    paddingTop: 54,
  },

  eyebrow: {
    ...typography.caption,
    color: colors.primaryBright,
    letterSpacing: 1.4,
  },

  title: {
    ...typography.h1,
    color: colors.text,
    marginTop: 4,
    marginBottom: spacing.lg,
  },

  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },

  avatar: {
    width: 72,
    height: 72,
    borderRadius: 24,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },

  avatarText: {
    fontSize: 24,
    fontWeight: '800',
    color: colors.white,
  },

  userInfo: {
    flex: 1,
  },

  profileName: {
  ...typography.h2,
  fontWeight: '700',
  color: colors.text,
},

  email: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: 2,
  },

  sport: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    marginTop: 8,
  },

  sportText: {
    ...typography.caption,
    color: colors.primaryBright,
  },

  card: {
    marginBottom: spacing.md,
  },
});