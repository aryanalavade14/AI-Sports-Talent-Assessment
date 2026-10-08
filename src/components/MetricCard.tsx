import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, spacing, typography } from '../theme';

export function MetricCard({ label, value, unit, accent = colors.primary }: { label: string; value: string; unit?: string; accent?: string }) {
  return (
    <View style={styles.card}>
      <View style={[styles.dot, { backgroundColor: accent }]} />
      <Text style={styles.label}>{label}</Text>
      <View style={styles.valueRow}>
        <Text style={styles.value}>{value}</Text>
        {unit ? <Text style={styles.unit}>{unit}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { flex: 1, backgroundColor: colors.surface, borderRadius: 20, borderWidth: 1, borderColor: colors.border, padding: spacing.md },
  dot: { width: 7, height: 7, borderRadius: 99, marginBottom: 10 },
  label: { ...typography.caption, color: colors.textMuted },
  valueRow: { flexDirection: 'row', alignItems: 'baseline', marginTop: 4, gap: 4 },
  value: { fontSize: 27, fontWeight: '800', color: colors.text },
  unit: { ...typography.caption, color: colors.textSecondary }
});