import React from 'react';
import { Pressable, StyleSheet, Text, View, ViewStyle } from 'react-native';
import { colors, shadows, spacing, typography } from '../theme';

interface Props {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
}

export function AppCard({ title, subtitle, icon, children, onPress, style }: Props) {
  const content = (
    <>
      {(title || icon) && (
        <View style={styles.header}>
          {icon ? <View style={styles.icon}>{icon}</View> : null}
          <View style={styles.headerText}>
            {title ? <Text style={styles.title}>{title}</Text> : null}
            {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
          </View>
        </View>
      )}
      {children}
    </>
  );

  return onPress ? (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.card, pressed && styles.pressed, style]}>
      {content}
    </Pressable>
  ) : (
    <View style={[styles.card, style]}>{content}</View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    ...shadows.card
  },
  pressed: { transform: [{ scale: 0.99 }], opacity: 0.94 },
  header: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  icon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center'
  },
  headerText: { flex: 1 },
  title: { ...typography.h3, color: colors.text },
  subtitle: { ...typography.caption, color: colors.textMuted, marginTop: 3 }
});