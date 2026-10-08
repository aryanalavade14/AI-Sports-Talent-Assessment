import React, { useCallback, useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

import { getHistory } from '../storage/storage';
import { initialHistory } from '../data/mockData';
import { colors, spacing, typography } from '../theme';
import { HistoryItem } from '../types';
import { EmptyState } from '../components/EmptyState';

export function HistoryScreen() {
  const [history, setHistory] =
    useState<HistoryItem[]>(removeDuplicates(initialHistory));

  useFocusEffect(
    useCallback(() => {
      getHistory().then((items) => {
        if (items.length > 0) {
          setHistory(removeDuplicates(items));
        } else {
          setHistory(removeDuplicates(initialHistory));
        }
      });
    }, [])
  );

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.eyebrow}>
        YOUR JOURNEY
      </Text>

      <Text style={styles.title}>
        Assessment history
      </Text>

      <Text style={styles.subtitle}>
        A simple record of your latest performance.
      </Text>

      {history.length === 0 ? (
        <EmptyState
          title="No assessments yet"
          message="Complete your first test and your result will appear here."
        />
      ) : (
        history.map((item) => (
          <View
            style={styles.item}
            key={item.id}
          >
            <View
              style={[
                styles.icon,
                {
                  backgroundColor:
                    item.testType === 'situp'
                      ? 'rgba(59,130,246,0.12)'
                      : 'rgba(139,92,246,0.12)',
                },
              ]}
            >
              <Ionicons
                name={
                  item.testType === 'situp'
                    ? 'fitness-outline'
                    : 'trending-up-outline'
                }
                size={22}
                color={
                  item.testType === 'situp'
                    ? colors.primaryBright
                    : colors.violet
                }
              />
            </View>

            <View style={styles.middle}>
              <Text style={styles.name}>
                {item.testType === 'situp'
                  ? 'Sit-ups'
                  : 'Vertical Jump'}
              </Text>

              <Text style={styles.meta}>
                {item.date} • {item.duration}
              </Text>
            </View>

            <View style={styles.result}>
              <Text style={styles.resultValue}>
                {item.result}
              </Text>

              <Text style={styles.resultUnit}>
                {item.unit}
              </Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}

/* ---------------------------------------------
   REMOVE DUPLICATE HISTORY ITEMS
--------------------------------------------- */

function removeDuplicates(
  items: HistoryItem[]
): HistoryItem[] {
  const seen = new Set<string>();

  return items.filter((item) => {
    const uniqueKey = [
      item.testType,
      item.result,
      item.unit,
      item.date,
      item.duration,
    ].join('|');

    if (seen.has(uniqueKey)) {
      return false;
    }

    seen.add(uniqueKey);
    return true;
  });
}

/* ---------------------------------------------
   STYLES
--------------------------------------------- */

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },

  content: {
    padding: spacing.lg,
    paddingTop: 54,
    paddingBottom: 40,
  },

  eyebrow: {
    ...typography.caption,
    color: colors.primaryBright,
    letterSpacing: 1.4,
  },

  title: {
    ...typography.h1,
    color: colors.text,
    marginTop: 4,
  },

  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: 5,
    marginBottom: spacing.xl,
  },

  item: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: 10,
  },

  icon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },

  middle: {
    flex: 1,
  },

  name: {
    ...typography.bodyMedium,
    color: colors.text,
  },

  meta: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: 3,
  },

  result: {
    alignItems: 'flex-end',
  },

  resultValue: {
    fontSize: 23,
    fontWeight: '800',
    color: colors.text,
  },

  resultUnit: {
    ...typography.caption,
    color: colors.textMuted,
  },
});