import { InjectionToken } from '@angular/core';
import { io, Socket } from 'socket.io-client';

export const SOCKET_IO_TOKEN = new InjectionToken<Socket>('SOCKET_IO_TOKEN', {
  providedIn: 'root',
  factory: () =>
    io({
      path: '/ws/socket.io/',
      withCredentials: true,
      autoConnect: true,
      reconnection: true,
    }),
});
