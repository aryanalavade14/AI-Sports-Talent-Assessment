import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { AppButton } from '../components/AppButton';
import { colors, spacing, typography } from '../theme';

const slides = [
  { icon: 'fitness-outline' as const, title: 'Measure your potential', text: 'Turn simple fitness tests into meaningful performance insights.' },
  { icon: 'camera-outline' as const, title: 'Assess with your phone', text: 'Follow guided camera-based tests designed for simple, repeatable assessment.' },
  { icon: 'sparkles-outline' as const, title: 'Train with confidence', text: 'Keep your results organized and build a clearer picture of your progress.' }
];

export function OnboardingScreen({ navigation }: any) {
  const [index, setIndex] = useState(0);
  const slide = slides[index];
  const last = index === slides.length - 1;

  return (
    <LinearGradient colors={[colors.background, '#0B1A31']} style={styles.container}>
      <View style={styles.top}><Text style={styles.brand}>SPORTS TALENT AI</Text><Text style={styles.step}>{index + 1}/{slides.length}</Text></View>
      <View style={styles.visual}>
        <View style={styles.orbit}><View style={styles.iconCircle}><Ionicons name={slide.icon} size={54} color={colors.white} /></View></View>
        <View style={styles.dotOne} /><View style={styles.dotTwo} />
      </View>
      <View style={styles.content}>
        <Text style={styles.title}>{slide.title}</Text>
        <Text style={styles.text}>{slide.text}</Text>
        <View style={styles.dots}>{slides.map((_, i) => <View key={i} style={[styles.dot, i === index && styles.activeDot]} />)}</View>
        <AppButton title={last ? 'Get Started' : 'Continue'} onPress={() => last ? navigation.replace('Auth') : setIndex(index + 1)} />
        {!last && <AppButton title="Skip" variant="ghost" onPress={() => navigation.replace('Auth')} />}
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.lg },
  top: { flexDirection: 'row', justifyContent: 'space-between', paddingTop: 20 },
  brand: { ...typography.caption, color: colors.primaryBright, letterSpacing: 1.2 },
  step: { ...typography.caption, color: colors.textMuted },
  visual: { flex: 1, alignItems: 'center', justifyContent: 'center', position: 'relative' },
  orbit: { width: 230, height: 230, borderRadius: 115, borderWidth: 1, borderColor: 'rgba(96,165,250,0.22)', alignItems: 'center', justifyContent: 'center' },
  iconCircle: { width: 140, height: 140, borderRadius: 48, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
  dotOne: { position: 'absolute', width: 12, height: 12, borderRadius: 6, backgroundColor: colors.cyan, top: 60, right: 75 },
  dotTwo: { position: 'absolute', width: 8, height: 8, borderRadius: 4, backgroundColor: colors.violet, bottom: 65, left: 70 },
  content: { paddingBottom: 18 },
  title: { ...typography.display, color: colors.text },
  text: { ...typography.body, color: colors.textSecondary, marginTop: 12, marginBottom: 24 },
  dots: { flexDirection: 'row', gap: 7, marginBottom: 24 },
  dot: { width: 7, height: 7, borderRadius: 7, backgroundColor: colors.surfaceLight },
  activeDot: { width: 24, backgroundColor: colors.primary },
});