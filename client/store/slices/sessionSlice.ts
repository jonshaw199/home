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
  data: {
    token?: string | null;
    profile?: string | null;
  };
  isLoading: boolean;
  error: string | null;
}

// Initial state for the slice
const initialState: SessionState = {
  data: {},
  isLoading: false,
  error: null,
};

// Thunks
export const signIn = createAsyncThunk<
  SessionState["data"],
  SignInProps,
  { state: RootState }
>(
  "session/signIn",
  async ({ username, password }, { rejectWithValue, dispatch, getState }) => {
    const url = selectBaseUrl(getState());
    if (!url) throw new Error("Base URL not set");

    try {
      const data = await getToken({ username, password, url });
      await setStorageItemAsync(storageKey, JSON.stringify(data));
      dispatch(setSession(data)); // Update session in the Redux state
      return data;
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
  const data = await getStorageItemAsync(storageKey);
  if (data) {
    try {
      const parsed = JSON.parse(data);
      const valid = await validateToken(parsed?.token);
      if (valid) {
        dispatch(setSession(parsed));
        return parsed;
      }
    } catch (e) {
      console.error("Error loading auth token from storage:", e);
    }
  }
  return {};
});

// Redux slice
const sessionSlice = createSlice({
  name: "session",
  initialState,
  reducers: {
    setSession: (state, action: PayloadAction<SessionState["data"]>) => {
      state.data = action.payload;
    },
    clearSession: (state) => {
      state.data = {};
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
        state.data = action.payload;
      })
      .addCase(signIn.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(signOut.fulfilled, (state) => {
        state.data = {};
        state.isLoading = false;
        setStorageItemAsync(storageKey, null);
      })
      // Experimental: log out on error
      .addCase(WS_ERROR, (state) => {
        console.warn("Logging out due to websocket error");
        state.data = {};
        state.isLoading = false;
        setStorageItemAsync(storageKey, null);
      });
  },
});

// Actions
export const { setSession, clearSession } = sessionSlice.actions;

// Selectors
export const selectSession = (state: RootState) => state.session.data;
export const selectIsLoading = (state: RootState) => state.session.isLoading;
export const selectError = (state: RootState) => state.session.error;

// Reducer
export const sessionSliceReducer = sessionSlice.reducer;
