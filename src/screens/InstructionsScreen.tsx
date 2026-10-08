import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppButton } from '../components/AppButton';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

export function InstructionsScreen({ navigation, route }: any) {
  const { testType } = route.params;
  const situp = testType === 'situp';
  const title = situp ? 'Sit-up assessment' : 'Vertical jump assessment';
  const steps = situp
    ? ['Place the phone where your full body is visible.', 'Start in a stable position on a clear surface.', 'Follow the countdown and perform controlled repetitions.', 'Keep your movement consistent until the recording ends.']
    : ['Place the phone so your full body and jump space are visible.', 'Stand upright with enough space above your head.', 'Follow the countdown and perform your maximum safe jump.', 'Land under control and wait for the recording to finish.'];

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <ScreenHeader title={title} subtitle="A quick guided setup before recording." onBack={() => navigation.goBack()} />
      <View style={styles.hero}><View style={styles.icon}><Ionicons name={situp ? 'fitness-outline' : 'trending-up-outline'} size={34} color={situp ? colors.primaryBright : colors.violet} /></View><Text style={styles.heroTitle}>{situp ? 'Focus on form, not speed.' : 'Explosive, controlled movement.'}</Text><Text style={styles.heroText}>{situp ? 'The demo counts your assessment using a mock AI result until the real CV service is connected.' : 'The mobile flow is ready for Pratham’s CV engine to return the final jump measurement.'}</Text></View>
      <Text style={styles.heading}>How to perform</Text>
      {steps.map((step, i) => <View style={styles.step} key={step}><View style={styles.number}><Text style={styles.numberText}>{i+1}</Text></View><Text style={styles.stepText}>{step}</Text></View>)}
      <AppButton title="Continue to checklist" onPress={() => navigation.navigate('Checklist', { testType })} style={styles.button} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 40 },
  hero: { margin: spacing.lg, padding: spacing.lg, backgroundColor: colors.surface, borderRadius: 26, borderWidth: 1, borderColor: colors.border },
  icon: { width: 62, height: 62, borderRadius: 20, backgroundColor: colors.surfaceLight, alignItems: 'center', justifyContent: 'center' },
  heroTitle: { ...typography.h2, color: colors.text, marginTop: spacing.md },
  heroText: { ...typography.body, color: colors.textSecondary, marginTop: 7 },
  heading: { ...typography.h2, color: colors.text, marginHorizontal: spacing.lg, marginBottom: spacing.md },
  step: { flexDirection: 'row', gap: 14, alignItems: 'center', marginHorizontal: spacing.lg, marginBottom: spacing.md },
  number: { width: 36, height: 36, borderRadius: 12, backgroundColor: 'rgba(59,130,246,0.14)', alignItems: 'center', justifyContent: 'center' },
  numberText: { ...typography.bodyMedium, color: colors.primaryBright },
  stepText: { ...typography.body, color: colors.textSecondary, flex: 1 },
  button: { marginHorizontal: spacing.lg, marginTop: spacing.lg }
});