// Telegram WebApp service with safe fallbacks
export interface TelegramUser {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  photoUrl?: string;
}

class TelegramService {
  private webApp: any = null;
  private initialized = false;

  constructor() {
    // Safely check if running in Telegram
    try {
      if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
        this.webApp = (window as any).Telegram.WebApp;
      }
    } catch (e) {
      console.log('Telegram WebApp not available, using fallback mode');
    }
  }

  init(): void {
    if (this.initialized) return;

    try {
      if (this.webApp) {
        this.webApp.ready();
        this.webApp.expand();
        this.webApp.setHeaderColor?.('secondary_bg_color');
        this.webApp.setBackgroundColor?.('#1a1a1a');
        this.initialized = true;
        console.log('Telegram WebApp initialized');
      } else {
        console.log('Running in standalone mode (not in Telegram)');
      }
    } catch (e) {
      console.error('Failed to initialize Telegram WebApp:', e);
    }
  }

  getUser(): TelegramUser | null {
    try {
      const user = this.webApp?.initDataUnsafe?.user;
      if (!user) return null;

      return {
        id: user.id,
        firstName: user.first_name,
        lastName: user.last_name,
        username: user.username,
        photoUrl: user.photo_url,
      };
    } catch (e) {
      return null;
    }
  }

  getUserId(): string {
    const user = this.getUser();
    return user ? user.id.toString() : `guest_${Date.now()}`;
  }

  getUserName(): string {
    const user = this.getUser();
    if (!user) return 'Guest';
    return user.username || user.firstName || 'Player';
  }

  showAlert(message: string): Promise<void> {
    return new Promise((resolve) => {
      try {
        if (this.webApp?.showAlert) {
          this.webApp.showAlert(message, resolve);
        } else {
          alert(message);
          resolve();
        }
      } catch (e) {
        alert(message);
        resolve();
      }
    });
  }

  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      try {
        if (this.webApp?.showConfirm) {
          this.webApp.showConfirm(message, resolve);
        } else {
          resolve(confirm(message));
        }
      } catch (e) {
        resolve(confirm(message));
      }
    });
  }

  hapticFeedback(type: 'impact' | 'notification' | 'selection', style?: string): void {
    try {
      if (!this.webApp?.HapticFeedback) return;

      if (type === 'impact' && style) {
        this.webApp.HapticFeedback.impactOccurred?.(style as 'light' | 'medium' | 'heavy');
      } else if (type === 'notification' && style) {
        this.webApp.HapticFeedback.notificationOccurred?.(style as 'error' | 'success' | 'warning');
      } else if (type === 'selection') {
        this.webApp.HapticFeedback.selectionChanged?.();
      }
    } catch (e) {
      // Haptic feedback is optional, silently fail
    }
  }

  close(): void {
    try {
      this.webApp?.close?.();
    } catch (e) {
      console.log('Cannot close, not in Telegram');
    }
  }

  isInTelegram(): boolean {
    return this.webApp !== null && this.webApp?.platform !== 'unknown';
  }

  getTheme(): 'light' | 'dark' {
    try {
      return this.webApp?.colorScheme === 'dark' ? 'dark' : 'light';
    } catch (e) {
      return 'dark';
    }
  }

  getInitData(): string {
    try {
      return this.webApp?.initData || '';
    } catch (e) {
      return '';
    }
  }
}

export const telegramService = new TelegramService();
