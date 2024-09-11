import { useContext, createContext, type PropsWithChildren } from "react";
import { useStorageState } from "@/hooks/useStorageState";
import { getToken } from "@/services/auth";

type AuthContextProps = {
  signIn: ({
    username,
    password,
  }: {
    username: string;
    password: string;
  }) => Promise<void>;
  signOut: () => void;
  session?: string | null;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextProps>({
  signIn: () => new Promise((_, rej) => rej()),
  signOut: () => null,
  session: null,
  isLoading: false,
});

// This hook can be used to access the user info.
export function useSession() {
  const value = useContext(AuthContext);

  if (process.env.NODE_ENV !== "production") {
    if (!value) {
      throw new Error("useSession must be wrapped in a <SessionProvider />");
    }
  }

  return value;
}

export function SessionProvider({ children }: PropsWithChildren) {
  const key = process.env.EXPO_PUBLIC_SESSION_STORAGE_KEY;
  if (!key) throw "Session storage key not found";

  const [[isLoading, session], setSession] = useStorageState(key);

  const signIn: AuthContextProps["signIn"] = async (props) => {
    const token = await getToken(props);
    setSession(token);
  };

  return (
    <AuthContext.Provider
      value={{
        signIn,
        signOut: () => {
          setSession(null);
        },
        session,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
