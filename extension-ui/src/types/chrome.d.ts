// Глобальные типы для Chrome API
export {};

declare global {
  var chrome: {
    storage: {
      local: {
        get: (keys: string[], callback: (result: Record<string, any>) => void) => void;
        set: (items: Record<string, any>, callback?: () => void) => void;
        remove: (keys: string[], callback?: () => void) => void;
      };
    };
    runtime: {
      lastError?: Error;
    };
    identity: {
      launchWebAuthFlow: (
        details: { url: string; interactive?: boolean },
        callback: (redirectUrl?: string) => void
      ) => void;
    };
  };
}
