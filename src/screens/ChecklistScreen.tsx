import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { AppButton } from '../components/AppButton';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

const items = ['Camera is ready', 'Enough clear space', 'Good lighting', 'Full body visible', 'Phone is stable'];

export function ChecklistScreen({ navigation, route }: any) {
  const { testType } = route.params;
  const [checked, setChecked] = useState<boolean[]>(items.map(() => false));
  const all = checked.every(Boolean);
  const toggle = (i: number) => setChecked(prev => prev.map((v, idx) => idx === i ? !v : v));
  return (
    <View style={styles.screen}>
      <ScreenHeader title="Pre-test checklist" subtitle="A few seconds for a better assessment." onBack={() => navigation.goBack()} />
      <View style={styles.container}>
        {items.map((item, i) => <View key={item} style={styles.item} onTouchEnd={() => toggle(i)}><View style={[styles.checkbox, checked[i] && styles.checked]}>{checked[i] && <Ionicons name="checkmark" size={16} color={colors.white} />}</View><Text style={styles.text}>{item}</Text></View>)}
        <View style={styles.info}><Ionicons name="information-circle-outline" size={20} color={colors.primaryBright} /><Text style={styles.infoText}>Your video stays on the device until the backend integration is connected.</Text></View>
        <AppButton title="Start assessment" onPress={() => navigation.navigate('Camera', { testType })} disabled={!all} style={styles.button} />
        {!all && <Text style={styles.helper}>Complete the checklist to continue.</Text>}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  container: { padding: spacing.lg },
  item: { flexDirection: 'row', alignItems: 'center', gap: 14, backgroundColor: colors.surface, borderRadius: 18, borderWidth: 1, borderColor: colors.border, padding: spacing.md, marginBottom: 10 },
  checkbox: { width: 28, height: 28, borderRadius: 9, borderWidth: 1.5, borderColor: colors.border, alignItems: 'center', justifyContent: 'center' },
  checked: { backgroundColor: colors.success, borderColor: colors.success },
  text: { ...typography.bodyMedium, color: colors.text },
  info: { flexDirection: 'row', gap: 10, marginTop: spacing.md, padding: spacing.md, borderRadius: 18, backgroundColor: 'rgba(59,130,246,0.07)' },
  infoText: { ...typography.caption, color: colors.textSecondary, flex: 1 },
  button: { marginTop: spacing.xl },
  helper: { ...typography.caption, color: colors.textMuted, textAlign: 'center', marginTop: 10 }
});