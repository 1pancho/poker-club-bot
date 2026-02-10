import WebApp from '@twa-dev/sdk';

export interface TelegramUser {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  photoUrl?: string;
}

class TelegramService {
  private webApp: typeof WebApp;
  private initialized = false;

  constructor() {
    this.webApp = WebApp;
  }

  init(): void {
    if (this.initialized) return;

    // Initialize Telegram WebApp
    this.webApp.ready();
    this.webApp.expand();

    // Set theme
    this.webApp.setHeaderColor('secondary_bg_color');
    this.webApp.setBackgroundColor('#1a1a1a');

    this.initialized = true;
    console.log('Telegram WebApp initialized');
  }

  getUser(): TelegramUser | null {
    const user = this.webApp.initDataUnsafe.user;
    if (!user) return null;

    return {
      id: user.id,
      firstName: user.first_name,
      lastName: user.last_name,
      username: user.username,
      photoUrl: user.photo_url,
    };
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
      this.webApp.showAlert(message, resolve);
    });
  }

  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      this.webApp.showConfirm(message, resolve);
    });
  }

  showPopup(title: string, message: string, buttons: { text: string; id: string }[]): Promise<string> {
    return new Promise((resolve) => {
      this.webApp.showPopup(
        {
          title,
          message,
          buttons: buttons.map(b => ({ type: 'default', text: b.text, id: b.id })),
        },
        (buttonId) => {
          resolve(buttonId || '');
        }
      );
    });
  }

  enableClosingConfirmation(): void {
    this.webApp.enableClosingConfirmation();
  }

  disableClosingConfirmation(): void {
    this.webApp.disableClosingConfirmation();
  }

  hapticFeedback(type: 'impact' | 'notification' | 'selection', style?: 'light' | 'medium' | 'heavy' | 'error' | 'success' | 'warning'): void {
    if (type === 'impact' && style) {
      this.webApp.HapticFeedback.impactOccurred(style as 'light' | 'medium' | 'heavy');
    } else if (type === 'notification' && style) {
      this.webApp.HapticFeedback.notificationOccurred(style as 'error' | 'success' | 'warning');
    } else if (type === 'selection') {
      this.webApp.HapticFeedback.selectionChanged();
    }
  }

  close(): void {
    this.webApp.close();
  }

  isInTelegram(): boolean {
    return this.webApp.platform !== 'unknown';
  }

  getTheme(): 'light' | 'dark' {
    return this.webApp.colorScheme === 'dark' ? 'dark' : 'light';
  }

  getInitData(): string {
    return this.webApp.initData;
  }
}

export const telegramService = new TelegramService();
