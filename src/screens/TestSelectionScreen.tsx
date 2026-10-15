import React from 'react';
import { ScrollView, StyleSheet, Text } from 'react-native';
import { TestCard } from '../components/TestCard';
import { ScreenHeader } from '../components/ScreenHeader';
import { testDefinitions } from '../data/mockData';
import { colors, spacing, typography } from '../theme';

export function TestSelectionScreen({ navigation }: any) {
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <ScreenHeader title="Choose your test" subtitle="Select an assessment to begin." onBack={() => navigation.goBack()} />
      <Text style={styles.note}>MVP assessments are guided and camera-based. Your results are saved locally when offline.</Text>
      {testDefinitions.map(test => <TestCard key={test.id} test={test} onPress={() => navigation.navigate('Instructions', { testType: test.id })} />)}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 40 },
  note: { ...typography.body, color: colors.textSecondary, marginHorizontal: spacing.lg, marginBottom: spacing.lg }
});