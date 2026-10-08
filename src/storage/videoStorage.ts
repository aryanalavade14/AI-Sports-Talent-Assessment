import * as FileSystem from 'expo-file-system/legacy';

export async function persistVideo(uri: string, sessionId: string): Promise<string> {
  const directory = `${FileSystem.documentDirectory ?? ''}assessments/`;
  const exists = await FileSystem.getInfoAsync(directory);
  if (!exists.exists) {
    await FileSystem.makeDirectoryAsync(directory, { intermediates: true });
  }
  const destination = `${directory}${sessionId}.mp4`;
  await FileSystem.copyAsync({ from: uri, to: destination });
  return destination;
}