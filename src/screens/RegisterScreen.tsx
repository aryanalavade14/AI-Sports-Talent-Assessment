import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';
import { GradientBackground } from '../components/GradientBackground';
import { AppButton } from '../components/AppButton';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

export function RegisterScreen({ navigation }: any) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  return (
    <GradientBackground>
      <ScreenHeader title="Create your profile" subtitle="Set up your athlete identity." onBack={() => navigation.goBack()} />
      <View style={styles.container}>
        <Text style={styles.label}>Full name</Text>
        <TextInput value={name} onChangeText={setName} placeholder="Arya Nalavade" placeholderTextColor={colors.textMuted} style={styles.input} />
        <Text style={styles.label}>Email</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@example.com" placeholderTextColor={colors.textMuted} style={styles.input} autoCapitalize="none" keyboardType="email-address" />
        <Text style={styles.label}>Password</Text>
        <TextInput placeholder="Create a password" placeholderTextColor={colors.textMuted} style={styles.input} secureTextEntry />
        <AppButton title="Create Athlete Profile" onPress={() => navigation.replace('Main')} style={styles.button} />
      </View>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: { padding: spacing.xl },
  label: { ...typography.caption, color: colors.textSecondary, marginBottom: 7, marginTop: spacing.md },
  input: { height: 54, borderRadius: 16, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, paddingHorizontal: 16, color: colors.text, fontSize: 15 },
  button: { marginTop: spacing.xl }
});