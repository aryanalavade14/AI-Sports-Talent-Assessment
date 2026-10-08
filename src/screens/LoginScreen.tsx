import React, { useState } from 'react';
import { Alert, StyleSheet, Text, TextInput, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { GradientBackground } from '../components/GradientBackground';
import { AppButton } from '../components/AppButton';
import { colors, spacing, typography } from '../theme';

export function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert(
        'Missing details',
        'Please enter your email and password.'
      );
      return;
    }

    // Convert email username into display name
    // Example: aayush@gmail.com → Aayush
    const emailName = email.trim().split('@')[0];

    const userName =
      emailName.length > 0
        ? emailName.charAt(0).toUpperCase() + emailName.slice(1)
        : 'Athlete';

    const user = {
      name: userName,
      email: email.trim().toLowerCase(),
      avatarInitials: userName.substring(0, 2).toUpperCase(),
    };

    try {
      await AsyncStorage.setItem(
        'loggedInUser',
        JSON.stringify(user)
      );

      navigation.replace('Main');
    } catch (error) {
      console.log('Login storage error:', error);

      Alert.alert(
        'Login Error',
        'Unable to save login details.'
      );
    }
  };

  return (
    <GradientBackground>
      <View style={styles.container}>

        <View style={styles.logo}>
          <Ionicons
            name="flash"
            size={28}
            color={colors.white}
          />
        </View>

        <Text style={styles.title}>
          Welcome back
        </Text>

        <Text style={styles.subtitle}>
          Sign in to continue your performance journey.
        </Text>

        <Text style={styles.label}>
          Email
        </Text>

        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={colors.textMuted}
          style={styles.input}
          autoCapitalize="none"
          keyboardType="email-address"
        />

        <Text style={styles.label}>
          Password
        </Text>

        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="••••••••"
          placeholderTextColor={colors.textMuted}
          style={styles.input}
          secureTextEntry
        />

        <AppButton
          title="Sign In"
          onPress={handleLogin}
          style={styles.button}
        />

        <Text style={styles.demo}>
          Demo mode • no backend required
        </Text>

        <View style={styles.signup}>
          <Text style={styles.secondary}>
            New athlete?
          </Text>

          <Text
            onPress={() => navigation.navigate('Register')}
            style={styles.link}
          >
            {' '}Create account
          </Text>
        </View>

      </View>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.xl,
    justifyContent: 'center',
  },

  logo: {
    width: 58,
    height: 58,
    borderRadius: 20,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xl,
  },

  title: {
    ...typography.display,
    color: colors.text,
  },

  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: 8,
    marginBottom: spacing.xl,
  },

  label: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: 7,
    marginTop: spacing.md,
  },

  input: {
    height: 54,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    color: colors.text,
    fontSize: 15,
  },

  button: {
    marginTop: spacing.xl,
  },

  demo: {
    ...typography.caption,
    color: colors.textMuted,
    textAlign: 'center',
    marginTop: 12,
  },

  signup: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing.xl,
  },

  secondary: {
    ...typography.body,
    color: colors.textSecondary,
  },

  link: {
    ...typography.bodyMedium,
    color: colors.primaryBright,
  },
});