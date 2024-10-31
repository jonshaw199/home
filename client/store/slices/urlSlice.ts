import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "@/store/index";

const apiPath = process.env.EXPO_PUBLIC_API_PATH;
if (!apiPath) throw "EXPO_PUBLIC_API_PATH not defined";
const wsPath = process.env.EXPO_PUBLIC_WS_PATH;
if (!wsPath) throw "EXPO_PUBLIC_WS_PATH not defined";
const healthCheckPath = process.env.EXPO_PUBLIC_HEALTH_CHECK_PATH;
if (!healthCheckPath) throw "EXPO_PUBLIC_HEALTH_CHECK_PATH not defined";

export type UrlState = {
  baseUrl?: string | null;
  availableUrls: string[];
  loading: boolean;
  error?: string | null;
};

const initialState: UrlState = {
  baseUrl: null,
  availableUrls: [
    process.env.EXPO_PUBLIC_LOCAL_BASE_URL || "",
    process.env.EXPO_PUBLIC_HOME_BASE_URL || "",
  ].filter(Boolean), // Only add non-empty URLs
  loading: true,
  error: null,
};

export const initializeBaseUrl = createAsyncThunk<void, void>(
  "url/initializeBaseUrl",
  async (_, { dispatch }) => {
    console.info("Finding reachable server...");

    const urls = initialState.availableUrls;

    // Find the first reachable URL
    for (const url of urls) {
      const healthCheckUrl = `${url}${healthCheckPath}`;
      try {
        const response = await fetch(healthCheckUrl);
        if (response.ok) {
          dispatch(urlSliceActions.setBaseUrl(url));
          return;
        }
      } catch (error) {
        console.warn(`Could not reach ${url}, trying next URL`);
      }
    }

    const msg = "No server URLs reachable!";
    console.error(msg);
  }
);

const urlSlice = createSlice({
  name: "url",
  initialState,
  reducers: {
    setBaseUrl: (state, action: PayloadAction<string>) => {
      state.baseUrl = action.payload;
    },
    selectBaseUrl: (state, action: PayloadAction<number>) => {
      // Select URL based on the provided index, if within range
      if (action.payload >= 0 && action.payload < state.availableUrls.length) {
        state.baseUrl = state.availableUrls[action.payload];
      }
    },
    rotateBaseUrl: (state) => {
      // Shift to the next available URL in a circular manner
      const currentIndex = state.baseUrl
        ? state.availableUrls.indexOf(state.baseUrl)
        : -1;
      const nextIndex = (currentIndex + 1) % state.availableUrls.length;
      state.baseUrl = state.availableUrls[nextIndex];
    },
    addBaseUrl: (state, action: PayloadAction<string>) => {
      // Add a new URL to the list if it's not already included
      if (!state.availableUrls.includes(action.payload)) {
        state.availableUrls.push(action.payload);
      }
    },
    removeBaseUrl: (state, action: PayloadAction<string>) => {
      // Remove a URL from the list and reset baseUrl if needed
      state.availableUrls = state.availableUrls.filter(
        (url) => url !== action.payload
      );
      if (state.baseUrl === action.payload) {
        state.baseUrl = state.availableUrls[0];
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(initializeBaseUrl.pending, (state) => {
      return {
        ...state,
        loading: true,
        error: null,
      };
    });
    builder.addCase(initializeBaseUrl.fulfilled, (state) => {
      return {
        ...state,
        loading: false,
        error: null,
      };
    });
    builder.addCase(initializeBaseUrl.rejected, (state, action) => {
      return {
        ...state,
        loading: false,
        error: action.error.message || "Failed to initialize base url",
      };
    });
  },
});

export const urlSliceActions = urlSlice.actions;
export const urlSliceReducer = urlSlice.reducer;

export const selectApiUrl = (state: RootState) => {
  const baseUrl = state.url.baseUrl;
  if (baseUrl) {
    return `${baseUrl}${apiPath}`;
  }
};

export const selectWebsocketUrl = (state: RootState) => {
  const baseUrl = state.url.baseUrl;
  // Covers http/ws and https/wss
  if (baseUrl?.startsWith("http")) {
    return `ws${baseUrl.substring(4)}${wsPath}`;
  }
};
