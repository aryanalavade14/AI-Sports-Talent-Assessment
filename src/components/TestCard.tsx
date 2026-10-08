import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppCard } from './AppCard';
import { colors, spacing, typography } from '../theme';
import { TestDefinition } from '../types';

export function TestCard({ test, onPress }: { test: TestDefinition; onPress: () => void }) {
  const icon = test.id === 'situp' ? 'fitness-outline' : 'trending-up-outline';
  return (
    <AppCard onPress={onPress} style={styles.card}>
      <View style={styles.row}>
        <View style={[styles.icon, { backgroundColor: `${test.accent}22` }]}>
          <Ionicons name={icon as any} size={27} color={test.accent} />
        </View>
        <View style={styles.content}>
          <Text style={styles.title}>{test.title}</Text>
          <Text style={styles.description} numberOfLines={2}>{test.description}</Text>
          <View style={styles.meta}>
            <View style={styles.metaItem}><Ionicons name="time-outline" size={14} color={colors.textMuted} /><Text style={styles.metaText}>{test.duration}</Text></View>
            <View style={styles.start}><Text style={styles.startText}>Start</Text><Ionicons name="arrow-forward" size={14} color={colors.primaryBright} /></View>
          </View>
        </View>
      </View>
    </AppCard>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: spacing.md },
  row: { flexDirection: 'row' },
  icon: { width: 58, height: 58, borderRadius: 18, alignItems: 'center', justifyContent: 'center', marginRight: spacing.md },
  content: { flex: 1 },
  title: { ...typography.h3, color: colors.text },
  description: { ...typography.body, color: colors.textSecondary, marginTop: 5 },
  meta: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: spacing.md },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 5 },
  metaText: { ...typography.caption, color: colors.textMuted },
  start: { flexDirection: 'row', alignItems: 'center', gap: 5 },
  startText: { ...typography.caption, color: colors.primaryBright }
});