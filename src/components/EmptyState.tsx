import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppButton } from './AppButton';
import { colors, spacing, typography } from '../theme';

export function EmptyState({ title, message, buttonTitle, onPress }: { title: string; message: string; buttonTitle?: string; onPress?: () => void }) {
  return (
    <View style={styles.container}>
      <View style={styles.icon}><Ionicons name="sparkles-outline" size={30} color={colors.primaryBright} /></View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
      {buttonTitle && onPress ? <AppButton title={buttonTitle} onPress={onPress} style={styles.button} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', padding: spacing.xl },
  icon: { width: 66, height: 66, borderRadius: 22, backgroundColor: 'rgba(59,130,246,0.12)', alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  title: { ...typography.h2, color: colors.text, textAlign: 'center' },
  message: { ...typography.body, color: colors.textSecondary, textAlign: 'center', marginTop: 8 },
  button: { marginTop: spacing.lg, minWidth: 180 }
});