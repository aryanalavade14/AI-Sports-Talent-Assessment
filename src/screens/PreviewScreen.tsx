import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { VideoView, useVideoPlayer } from 'expo-video';
import { AppButton } from '../components/AppButton';
import { ScreenHeader } from '../components/ScreenHeader';
import { colors, spacing, typography } from '../theme';

export function PreviewScreen({ navigation, route }: any) {
  const { testType, videoUri } = route.params;
  const [ready, setReady] = useState(true);
  const player = useVideoPlayer(videoUri, (p) => { p.loop = false; });

  return (
    <View style={styles.screen}>
      <ScreenHeader title="Review recording" subtitle="Make sure your movement is clearly visible." onBack={() => navigation.goBack()} />
      <View style={styles.videoWrap}>
        {ready ? <VideoView player={player} style={styles.video} contentFit="cover" nativeControls /> : <Text style={styles.text}>Video unavailable</Text>}
      </View>
      <View style={styles.bottom}>
        <Text style={styles.title}>Ready to analyze?</Text>
        <Text style={styles.text}>You can retake the recording if your full body was not visible.</Text>
        <AppButton title="Confirm & Analyze" onPress={() => navigation.replace('Processing', { testType, videoUri })} style={styles.button} />
        <AppButton title="Retake" variant="secondary" onPress={() => navigation.replace('Camera', { testType })} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  videoWrap: { marginHorizontal: spacing.lg, height: 430, borderRadius: 28, overflow: 'hidden', backgroundColor: colors.black, borderWidth: 1, borderColor: colors.border },
  video: { flex: 1 },
  bottom: { padding: spacing.lg },
  title: { ...typography.h2, color: colors.text },
  text: { ...typography.body, color: colors.textSecondary, marginTop: 6 },
  button: { marginTop: spacing.xl, marginBottom: spacing.sm }
});