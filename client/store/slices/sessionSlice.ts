// sessionSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { getToken, validateToken } from "@/services/auth";
import { RootState } from "@/store"; // Assuming your Redux store is set up to export RootState
import {
  getStorageItemAsync,
  setStorageItemAsync,
} from "@/hooks/useStorageState";
import { WS_ERROR } from "@/ws/websocketActionTypes";
import { selectBaseUrl } from "./urlSlice";

const storageKey = process.env.EXPO_PUBLIC_SESSION_STORAGE_KEY;
if (!storageKey) throw "EXPO_PUBLIC_SESSION_STORAGE_KEY must be defined";

// Type definitions
interface SignInProps {
  username: string;
  password: string;
}

export interface SessionState {
  session: string | null;
  isLoading: boolean;
  error: string | null;
}

// Initial state for the slice
const initialState: SessionState = {
  session: null,
  isLoading: false,
  error: null,
};

// Thunks
export const signIn = createAsyncThunk<
  string,
  SignInProps,
  { state: RootState }
>(
  "session/signIn",
  async ({ username, password }, { rejectWithValue, dispatch, getState }) => {
    const url = selectBaseUrl(getState());
    if (!url) throw new Error("Base URL not set");

    try {
      const token = await getToken({ username, password, url });
      await setStorageItemAsync(storageKey, token);
      dispatch(setSession(token)); // Update session in the Redux state
      return token;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const signOut = createAsyncThunk<void, void, { state: RootState }>(
  "session/signOut",
  async (_, { dispatch }) => {
    dispatch(clearSession()); // Clear session from Redux state
    await setStorageItemAsync(storageKey, null);
  }
);

export const loadFromStorage = createAsyncThunk<
  string | null,
  void,
  { state: RootState }
>("session/loadFromStorage", async (_, { dispatch }) => {
  const token = await getStorageItemAsync(storageKey);
  if (token) {
    const valid = await validateToken(token);
    if (valid) {
      dispatch(setSession(token));
      return token;
    } else {
      await setStorageItemAsync(storageKey, null);
    }
  }
  return null;
});

// Redux slice
const sessionSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    setSession: (state, action: PayloadAction<string | null>) => {
      state.session = action.payload;
    },
    clearSession: (state) => {
      state.session = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(signIn.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(signIn.fulfilled, (state, action) => {
        state.isLoading = false;
        state.session = action.payload;
      })
      .addCase(signIn.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(signOut.fulfilled, (state) => {
        state.session = null;
        state.isLoading = false;
      })
      // Experimental: log out on error
      .addCase(WS_ERROR, (state) => {
        console.warn("Logging out due to websocket error");
        state.session = null;
        state.isLoading = false;
        setStorageItemAsync(storageKey, null);
      });
  },
});

// Actions
export const { setSession, clearSession } = sessionSlice.actions;

// Selectors
export const selectSession = (state: RootState) => state.session.session;
export const selectIsLoading = (state: RootState) => state.session.isLoading;
export const selectError = (state: RootState) => state.session.error;

// Reducer
export const sessionSliceReducer = sessionSlice.reducer;
