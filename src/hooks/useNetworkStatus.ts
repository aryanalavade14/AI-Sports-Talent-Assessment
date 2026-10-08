import { useEffect, useState } from 'react';
import NetInfo from '@react-native-community/netinfo';
import { NetworkStatus } from '../types';

export function useNetworkStatus(): NetworkStatus {
  const [status, setStatus] = useState<NetworkStatus>('online');

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setStatus(state.isConnected ? 'online' : 'offline');
    });

    NetInfo.fetch().then((state) => {
      setStatus(state.isConnected ? 'online' : 'offline');
    });

    return unsubscribe;
  }, []);

  return status;
}