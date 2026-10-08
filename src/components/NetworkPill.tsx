import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography } from '../theme';
import { NetworkStatus } from '../types';

export function NetworkPill({ status }: { status: NetworkStatus }) {
  const online = status === 'online';
  return (
    <View style={[styles.pill, online ? styles.online : styles.offline]}>
      <Ionicons name={online ? 'cloud-done-outline' : 'cloud-offline-outline'} size={14} color={online ? colors.success : colors.warning} />
      <Text style={styles.text}>{online ? 'Online' : 'Offline • Saved locally'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: { alignSelf: 'flex-start', flexDirection: 'row', alignItems: 'center', gap: 6, borderRadius: 999, paddingHorizontal: 11, paddingVertical: 7, borderWidth: 1 },
  online: { backgroundColor: 'rgba(34,197,94,0.08)', borderColor: 'rgba(34,197,94,0.22)' },
  offline: { backgroundColor: 'rgba(245,158,11,0.08)', borderColor: 'rgba(245,158,11,0.22)' },
  text: { ...typography.caption, color: colors.textSecondary }
});