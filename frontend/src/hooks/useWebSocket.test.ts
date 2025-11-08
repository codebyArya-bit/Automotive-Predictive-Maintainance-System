import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import useWebSocket from './useWebSocket';

class MockWebSocket {
  static OPEN = 1;
  static CLOSED = 3;
  readyState = MockWebSocket.OPEN;
  onopen: ((e: Event) => void) | null = null;
  onclose: ((e: CloseEvent) => void) | null = null;
  onerror: ((e: Event) => void) | null = null;
  onmessage: ((e: MessageEvent) => void) | null = null;
  constructor(public url: string) {}
  send(_data: any) {}
  close() { this.readyState = MockWebSocket.CLOSED; }
}

describe('useWebSocket', () => {
  beforeEach(() => {
    (global as any).WebSocket = MockWebSocket as any;
  });

  it('logs error on socket error', async () => {
    const logError = vi.spyOn((await import('../utils/errorHandler')), 'logError');
    const logWebSocketError = vi.spyOn((await import('../utils/logger')), 'logWebSocketError').mockResolvedValue();

    // Trigger socket error automatically on construction
    class ErrorMockWebSocket extends MockWebSocket {
      constructor(url: string) {
        super(url);
        setTimeout(() => {
          this.onerror?.(new Event('error'));
        }, 0);
      }
    }
    (global as any).WebSocket = ErrorMockWebSocket as any;

    renderHook(() => useWebSocket('ws://localhost:8000/ws/demo'));

    await waitFor(() => {
      expect(logError).toHaveBeenCalled();
      expect(logWebSocketError).toHaveBeenCalled();
    });
  });
});