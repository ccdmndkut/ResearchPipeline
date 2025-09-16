import { useState, useEffect, useRef } from 'react';
import io, { Socket } from 'socket.io-client';

const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!url) return;

    const socket = io(url);
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    });

    socket.on('message', (message: any) => {
      setLastMessage(message);
    });

    return () => {
      socket.disconnect();
    };
  }, [url]);

  const sendMessage = (message: any) => {
    socketRef.current?.emit('message', message);
  };

  return { isConnected, lastMessage, sendMessage };
};

export default useWebSocket;
