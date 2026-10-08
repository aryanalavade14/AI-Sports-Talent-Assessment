import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { analyzeTest } from '../services/mockApi';
import { addHistoryItem } from '../storage/storage';
import { persistVideo } from '../storage/videoStorage';
import { colors, spacing, typography } from '../theme';

export function ProcessingScreen({ navigation, route }: any) {
  const { testType, videoUri } = route.params;
  const [step, setStep] = useState(0);
  const steps = ['Securing your recording', 'Preparing assessment', 'Generating performance result'];

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      for (let i = 0; i < steps.length; i++) {
        if (cancelled) return;
        setStep(i);
        await new Promise(resolve => setTimeout(resolve, 650));
      }
      let storedUri: string | undefined;
      if (videoUri) {
        try { storedUri = await persistVideo(videoUri, `${testType}-${Date.now()}`); } catch {}
      }
      const result = await analyzeTest(testType, storedUri);
      const numeric = result.test_type === 'situp' ? result.repetitions : result.jump_height_cm;
      await addHistoryItem({
        id: `${Date.now()}`,
        testType,
        result: numeric,
        unit: result.test_type === 'situp' ? 'reps' : 'cm',
        date: 'Just now',
        duration: testType === 'situp' ? '01:00' : '00:45',
        syncStatus: 'pending'
      });
      if (!cancelled) navigation.replace('Result', { testType, result, durationSeconds: testType === 'situp' ? 60 : 45 });
    };
    run();
    return () => { cancelled = true; };
  }, []);

  return (
    <View style={styles.screen}>
      <View style={styles.orbit}><View style={styles.inner}><Ionicons name="sparkles" size={32} color={colors.white} /></View></View>
      <Text style={styles.title}>Analyzing your assessment</Text>
      <Text style={styles.subtitle}>Your mobile demo is using a mock AI service. The real CV engine can be connected later.</Text>
      <View style={styles.steps}>{steps.map((item, i) => <View key={item} style={styles.row}><View style={[styles.check, i <= step && styles.active]}>{i < step ? <Ionicons name="checkmark" size={13} color={colors.white} /> : <Text style={styles.number}>{i+1}</Text>}</View><Text style={[styles.stepText, i === step && styles.current]}>{item}</Text></View>)}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  orbit: { width: 122, height: 122, borderRadius: 61, borderWidth: 1, borderColor: 'rgba(96,165,250,0.3)', alignItems: 'center', justifyContent: 'center', marginBottom: spacing.xl },
  inner: { width: 82, height: 82, borderRadius: 30, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
  title: { ...typography.h1, color: colors.text, textAlign: 'center' },
  subtitle: { ...typography.body, color: colors.textSecondary, textAlign: 'center', marginTop: 10 },
  steps: { alignSelf: 'stretch', marginTop: spacing.xl },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 13 },
  check: { width: 30, height: 30, borderRadius: 10, borderWidth: 1, borderColor: colors.border, alignItems: 'center', justifyContent: 'center' },
  active: { backgroundColor: colors.primary, borderColor: colors.primary },
  number: { ...typography.caption, color: colors.textMuted },
  stepText: { ...typography.body, color: colors.textMuted },
  current: { color: colors.text }
});