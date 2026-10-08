import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { AppButton } from '../components/AppButton';
import { MetricCard } from '../components/MetricCard';
import { colors, spacing, typography } from '../theme';

export function ResultScreen({ navigation, route }: any) {
  const { testType, result, durationSeconds } = route.params;
  const situp = testType === 'situp';
  const value = situp ? result.repetitions : result.jump_height_cm;
  const unit = situp ? 'reps' : 'cm';
  const label = situp ? 'SIT-UPS' : 'VERTICAL JUMP';
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <LinearGradient colors={situp ? ['#104E9E', '#273A93'] : ['#4C2D8E', '#243E89']} style={styles.hero}>
        <View style={styles.success}><Ionicons name="checkmark" size={24} color={colors.white} /></View>
        <Text style={styles.complete}>ASSESSMENT COMPLETE</Text>
        <Text style={styles.value}>{value}</Text>
        <Text style={styles.unit}>{label}</Text>
        <View style={styles.status}><Text style={styles.statusText}>Verified demo result</Text></View>
      </LinearGradient>
      <Text style={styles.sectionTitle}>Performance summary</Text>
      <View style={styles.metrics}><MetricCard label="Result" value={String(value)} unit={unit} accent={situp ? colors.primaryBright : colors.violet} /><MetricCard label="Duration" value={String(Math.round((durationSeconds ?? 60)/60)).padStart(2,'0')} unit="min" accent={colors.cyan} /></View>
      <View style={styles.note}><Ionicons name="information-circle-outline" size={20} color={colors.primaryBright} /><Text style={styles.noteText}>This is a mock AI result for the mobile demonstration. It is ready to be replaced by the team's real analysis service.</Text></View>
      <AppButton title="Save & return home" onPress={() => navigation.popToTop()} style={styles.button} />
      <AppButton title="Try again" variant="secondary" onPress={() => navigation.replace('Instructions', { testType })} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: 40 },
  hero: { borderRadius: 30, padding: spacing.xl, alignItems: 'center', marginBottom: spacing.xl },
  success: { width: 50, height: 50, borderRadius: 18, backgroundColor: 'rgba(34,197,94,0.95)', alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md },
  complete: { ...typography.caption, color: 'rgba(255,255,255,0.75)', letterSpacing: 1.8 },
  value: { fontSize: 76, lineHeight: 82, fontWeight: '900', color: colors.white, marginTop: 8 },
  unit: { ...typography.bodyMedium, color: colors.white, letterSpacing: 1.8 },
  status: { marginTop: spacing.md, backgroundColor: 'rgba(255,255,255,0.12)', paddingHorizontal: 12, paddingVertical: 7, borderRadius: 999 },
  statusText: { ...typography.caption, color: colors.white },
  sectionTitle: { ...typography.h2, color: colors.text, marginBottom: spacing.md },
  metrics: { flexDirection: 'row', gap: spacing.md },
  note: { flexDirection: 'row', gap: 10, padding: spacing.md, borderRadius: 18, backgroundColor: 'rgba(59,130,246,0.07)', marginTop: spacing.lg },
  noteText: { ...typography.caption, color: colors.textSecondary, flex: 1 },
  button: { marginTop: spacing.xl, marginBottom: spacing.sm }
});