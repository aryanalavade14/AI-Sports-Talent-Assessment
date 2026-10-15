import React, { useEffect, useRef, useState } from 'react';
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Alert,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography } from '../theme';

export function CameraScreen({ navigation, route }: any) {
  const { testType } = route.params;

  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  const [cameraReady, setCameraReady] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(3);
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);

  // ---------------------------------------------
  // COUNTDOWN
  // ---------------------------------------------

  useEffect(() => {
    if (!permission?.granted) {
      return;
    }

    if (countdown === null) {
      return;
    }

    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown((previous) => {
          if (previous === null) {
            return null;
          }

          return previous - 1;
        });
      }, 1000);

      return () => clearTimeout(timer);
    }

    if (countdown === 0 && cameraReady && !recording) {
      startRecording();
    }
  }, [countdown, permission?.granted, cameraReady, recording]);

  // ---------------------------------------------
  // RECORDING TIMER
  // ---------------------------------------------

  useEffect(() => {
    if (!recording) {
      return;
    }

    const timer = setInterval(() => {
      setSeconds((previous) => previous + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [recording]);

  // ---------------------------------------------
  // START RECORDING
  // ---------------------------------------------

  async function startRecording() {
    if (!cameraRef.current) {
      Alert.alert(
        'Camera not ready',
        'Please wait a moment and try again.'
      );
      return;
    }

    if (!cameraReady) {
      Alert.alert(
        'Camera not ready',
        'Please wait for the camera to initialize.'
      );
      return;
    }

    if (recording) {
      return;
    }

    try {
      setRecording(true);
      setSeconds(0);

      const result = await cameraRef.current.recordAsync({
        maxDuration: 60,
      });

      setRecording(false);

      if (result?.uri) {
        navigation.replace('Preview', {
          testType,
          videoUri: result.uri,
        });
      } else {
        Alert.alert(
          'Recording problem',
          'The video could not be saved. Please try again.'
        );
      }
    } catch (error) {
      console.log('Recording error:', error);

      setRecording(false);

      Alert.alert(
        'Recording failed',
        'The camera could not start recording. Please try again.'
      );
    }
  }

  // ---------------------------------------------
  // STOP RECORDING
  // ---------------------------------------------

  function stopRecording() {
    if (!recording) {
      return;
    }

    cameraRef.current?.stopRecording();
  }

  // ---------------------------------------------
  // PERMISSION CHECK
  // ---------------------------------------------

  if (!permission) {
    return (
      <View style={styles.center}>
        <Text style={styles.text}>
          Checking camera permission...
        </Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <View style={styles.permissionIcon}>
          <Ionicons
            name="camera-outline"
            size={38}
            color={colors.primaryBright}
          />
        </View>

        <Text style={styles.title}>
          Camera access needed
        </Text>

        <Text style={styles.text}>
          Your camera is used only to record the assessment video.
        </Text>

        <TouchableOpacity
          style={styles.permissionButton}
          onPress={requestPermission}
        >
          <Text style={styles.buttonText}>
            Allow camera
          </Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.cancel}>
            Go back
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  const minutes = String(Math.floor(seconds / 60)).padStart(2, '0');
  const remainingSeconds = String(seconds % 60).padStart(2, '0');

  return (
    <View style={styles.screen}>

      {/* CAMERA */}
      <CameraView
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        facing="back"
        mode="video"
        mute={true}
        onCameraReady={() => {
          console.log('Camera is ready');
          setCameraReady(true);
        }}
      />

      {/* DARK OVERLAY */}
      <View style={styles.overlay}>

        {/* TOP BAR */}
        <View style={styles.top}>

          <TouchableOpacity
            style={styles.close}
            disabled={recording}
            onPress={() => navigation.goBack()}
          >
            <Ionicons
              name="close"
              size={24}
              color={colors.white}
            />
          </TouchableOpacity>

          <View style={styles.testPill}>
            <Text style={styles.testText}>
              {testType === 'situp'
                ? 'SIT-UPS'
                : 'VERTICAL JUMP'}
            </Text>
          </View>

          <View style={styles.closeGhost} />
        </View>

        {/* CAMERA FRAME */}
        <View style={styles.guide}>

          <View style={styles.cornerTL} />
          <View style={styles.cornerTR} />
          <View style={styles.cornerBL} />
          <View style={styles.cornerBR} />

          {/* CAMERA NOT READY */}
          {!cameraReady && (
            <View style={styles.centerMessage}>
              <Text style={styles.readyText}>
                Preparing camera...
              </Text>
            </View>
          )}

          {/* COUNTDOWN */}
          {cameraReady &&
            countdown !== null &&
            countdown > 0 &&
            !recording && (
              <View style={styles.count}>
                <Text style={styles.countText}>
                  {countdown}
                </Text>

                <Text style={styles.countLabel}>
                  GET READY
                </Text>
              </View>
            )}

          {/* GO */}
          {cameraReady &&
            countdown === 0 &&
            !recording && (
              <View style={styles.count}>
                <Text style={styles.goText}>
                  GO!
                </Text>
              </View>
            )}

          {/* RECORDING STATUS */}
          {recording && (
            <View style={styles.recordingStatus}>
              <View style={styles.redDot} />

              <Text style={styles.recordingText}>
                RECORDING
              </Text>
            </View>
          )}
        </View>

        {/* BOTTOM */}
        <View style={styles.bottom}>

          <Text style={styles.instruction}>
            {recording
              ? 'Keep moving with controlled form.'
              : 'Position your full body inside the frame.'}
          </Text>

          {/* RECORDING BUTTON */}
          {recording ? (
            <TouchableOpacity
              style={styles.recordingButton}
              onPress={stopRecording}
            >
              <View style={styles.stopSquare} />

              <Text style={styles.timer}>
                {minutes}:{remainingSeconds}
              </Text>
            </TouchableOpacity>
          ) : (
            <View style={styles.recordButton}>
              <View style={styles.innerRecord} />
            </View>
          )}

        </View>
      </View>
    </View>
  );
}

// ---------------------------------------------
// STYLES
// ---------------------------------------------

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.black,
  },

  center: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 28,
  },

  permissionIcon: {
    width: 76,
    height: 76,
    borderRadius: 26,
    backgroundColor: 'rgba(59,130,246,0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
  },

  title: {
    ...typography.h1,
    color: colors.text,
    textAlign: 'center',
  },

  text: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 10,
  },

  permissionButton: {
    marginTop: 24,
    backgroundColor: colors.primary,
    paddingHorizontal: 26,
    paddingVertical: 15,
    borderRadius: 16,
  },

  buttonText: {
    ...typography.bodyMedium,
    color: colors.white,
  },

  cancel: {
    ...typography.bodyMedium,
    color: colors.primaryBright,
    marginTop: 18,
  },

  overlay: {
    flex: 1,
    justifyContent: 'space-between',
    padding: 22,
    paddingTop: 56,
    paddingBottom: 34,
  },

  top: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  close: {
    width: 42,
    height: 42,
    borderRadius: 14,
    backgroundColor: 'rgba(0,0,0,0.38)',
    alignItems: 'center',
    justifyContent: 'center',
  },

  closeGhost: {
    width: 42,
  },

  testPill: {
    backgroundColor: 'rgba(0,0,0,0.45)',
    paddingHorizontal: 13,
    paddingVertical: 8,
    borderRadius: 999,
  },

  testText: {
    ...typography.caption,
    color: colors.white,
    letterSpacing: 1,
  },

  guide: {
    flex: 1,
    marginVertical: 70,
    position: 'relative',
    borderColor: 'rgba(255,255,255,0.28)',
    borderWidth: 1,
    borderRadius: 28,
  },

  cornerTL: {
    position: 'absolute',
    left: -1,
    top: -1,
    width: 38,
    height: 38,
    borderLeftWidth: 3,
    borderTopWidth: 3,
    borderColor: colors.cyan,
    borderTopLeftRadius: 26,
  },

  cornerTR: {
    position: 'absolute',
    right: -1,
    top: -1,
    width: 38,
    height: 38,
    borderRightWidth: 3,
    borderTopWidth: 3,
    borderColor: colors.cyan,
    borderTopRightRadius: 26,
  },

  cornerBL: {
    position: 'absolute',
    left: -1,
    bottom: -1,
    width: 38,
    height: 38,
    borderLeftWidth: 3,
    borderBottomWidth: 3,
    borderColor: colors.cyan,
    borderBottomLeftRadius: 26,
  },

  cornerBR: {
    position: 'absolute',
    right: -1,
    bottom: -1,
    width: 38,
    height: 38,
    borderRightWidth: 3,
    borderBottomWidth: 3,
    borderColor: colors.cyan,
    borderBottomRightRadius: 26,
  },

  count: {
    position: 'absolute',
    alignSelf: 'center',
    top: '40%',
    alignItems: 'center',
  },

  countText: {
    fontSize: 84,
    fontWeight: '900',
    color: colors.white,
  },

  goText: {
    fontSize: 70,
    fontWeight: '900',
    color: colors.white,
  },

  countLabel: {
    ...typography.caption,
    color: colors.white,
    letterSpacing: 2,
  },

  centerMessage: {
    position: 'absolute',
    top: '45%',
    alignSelf: 'center',
  },

  readyText: {
    color: colors.white,
    fontSize: 18,
    fontWeight: '700',
  },

  recordingStatus: {
    position: 'absolute',
    top: 20,
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.65)',
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 20,
  },

  redDot: {
    width: 9,
    height: 9,
    borderRadius: 5,
    backgroundColor: colors.danger,
    marginRight: 8,
  },

  recordingText: {
    color: colors.white,
    fontWeight: '800',
    letterSpacing: 1,
  },

  bottom: {
    alignItems: 'center',
  },

  instruction: {
    ...typography.bodyMedium,
    color: colors.white,
    backgroundColor: 'rgba(0,0,0,0.45)',
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 12,
    marginBottom: 18,
  },

  recordButton: {
    width: 78,
    height: 78,
    borderRadius: 39,
    borderWidth: 5,
    borderColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
  },

  innerRecord: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.danger,
  },

  recordingButton: {
    width: 84,
    height: 84,
    borderRadius: 42,
    borderWidth: 4,
    borderColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(239,68,68,0.8)',
  },

  stopSquare: {
    width: 25,
    height: 25,
    borderRadius: 5,
    backgroundColor: colors.white,
  },

  timer: {
    position: 'absolute',
    top: -30,
    color: colors.white,
    fontWeight: '800',
  },
});