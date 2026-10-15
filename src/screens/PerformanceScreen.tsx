import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MetricCard } from '../components/MetricCard';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

export function PerformanceScreen({ navigation }: any) {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <ScreenHeader title="Performance" subtitle="Your assessment snapshot." onBack={() => navigation.goBack()} />
      <View style={styles.metrics}><MetricCard label="Tests completed" value="2" /><MetricCard label="Best sit-ups" value="32" unit="reps" accent={colors.cyan} /></View>
      <View style={styles.metrics}><MetricCard label="Best jump" value="46" unit="cm" accent={colors.violet} /><MetricCard label="Latest status" value="OK" accent={colors.success} /></View>
      <View style={styles.card}><View style={styles.icon}><Ionicons name="sparkles-outline" size={23} color={colors.primaryBright}/></View><Text style={styles.title}>Built for progress</Text><Text style={styles.text}>Benchmarking and percentile insights can be connected here later by the team’s benchmarking module.</Text></View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 40 },
  metrics: { flexDirection: 'row', gap: spacing.md, marginHorizontal: spacing.lg, marginBottom: spacing.md },
  card: { margin: spacing.lg, marginTop: spacing.md, backgroundColor: colors.surface, borderRadius: 24, borderWidth: 1, borderColor: colors.border, padding: spacing.lg },
  icon: { width: 46, height: 46, borderRadius: 15, backgroundColor: 'rgba(59,130,246,0.12)', alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  title: { ...typography.h2, color: colors.text },
  text: { ...typography.body, color: colors.textSecondary, marginTop: 6 }
});