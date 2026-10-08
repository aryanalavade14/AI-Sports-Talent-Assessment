import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography } from '../theme';

export function SplashScreen() {
  return (
    <LinearGradient colors={[colors.background, '#0A1A32', '#11162E']} style={styles.container}>
      <View style={styles.logo}><Ionicons name="flash" size={34} color={colors.white} /></View>
      <Text style={styles.brand}>SPORTS TALENT AI</Text>
      <Text style={styles.tagline}>Discover Your Potential.</Text>
      <View style={styles.bottom}><View style={styles.line} /><Text style={styles.caption}>AI-ASSISTED PERFORMANCE</Text></View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  logo: { width: 82, height: 82, borderRadius: 28, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.lg },
  brand: { ...typography.h1, color: colors.white, letterSpacing: 1.2 },
  tagline: { ...typography.body, color: colors.textSecondary, marginTop: 8 },
  bottom: { position: 'absolute', bottom: 48, alignItems: 'center' },
  line: { width: 44, height: 3, borderRadius: 3, backgroundColor: colors.cyan, marginBottom: 10 },
  caption: { ...typography.caption, color: colors.textMuted, letterSpacing: 1.5 }
});