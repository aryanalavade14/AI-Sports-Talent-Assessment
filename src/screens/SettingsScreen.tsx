import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppCard } from '../components/AppCard';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

export function SettingsScreen({ navigation }: any) {
  return (
    <View style={styles.screen}>
      <ScreenHeader title="Settings" subtitle="Keep your experience simple." onBack={() => navigation.goBack()} />
      <AppCard title="Offline-first storage" subtitle="Assessment recordings are kept locally for the demo." icon={<Ionicons name="phone-portrait-outline" size={22} color={colors.primaryBright} />} style={styles.card} />
      <AppCard title="API integration" subtitle="Mock service active • ready for backend integration" icon={<Ionicons name="git-network-outline" size={22} color={colors.violet} />} style={styles.card} />
      <AppCard title="About SPORTS TALENT AI" subtitle="AI-assisted sports talent assessment" icon={<Ionicons name="information-circle-outline" size={22} color={colors.textSecondary} />} />
      <Text style={styles.version}>Version 1.0.0 • Mobile MVP</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  card: { marginHorizontal: spacing.lg, marginBottom: spacing.md },
  version: { ...typography.caption, color: colors.textMuted, textAlign: 'center', marginTop: spacing.xl }
});