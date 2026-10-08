import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  ViewStyle,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { colors, shadows, spacing, typography } from '../theme';

interface Props {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
}

export function AppButton({
  title,
  onPress,
  variant = 'primary',
  disabled,
  loading,
  style,
}: Props) {
  const isWhiteButton =
    style?.backgroundColor === colors.white;

  const handlePress = async () => {
    await Haptics.impactAsync(
      Haptics.ImpactFeedbackStyle.Light
    );

    onPress();
  };

  return (
    <Pressable
      onPress={handlePress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.base,

        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'ghost' && styles.ghost,

        isWhiteButton && styles.whiteButton,

        (disabled || loading) && styles.disabled,

        pressed && styles.pressed,

        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator
          color={
            isWhiteButton
              ? colors.primary
              : colors.white
          }
        />
      ) : (
        <Text
          style={[
            styles.text,
            isWhiteButton && styles.whiteButtonText,
          ]}
        >
          {title}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 54,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    flexDirection: 'row',
  },

  primary: {
    backgroundColor: colors.primary,
    ...shadows.button,
  },

  secondary: {
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: colors.border,
  },

  ghost: {
    backgroundColor: 'transparent',
  },

  whiteButton: {
    backgroundColor: colors.white,
  },

  text: {
    ...typography.bodyMedium,
    color: colors.white,
    textAlign: 'center',
  },

  whiteButtonText: {
    color: colors.primary,
  },

  disabled: {
    opacity: 0.5,
  },

  pressed: {
    transform: [{ scale: 0.985 }],
  },
});