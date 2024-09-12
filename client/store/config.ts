import { Device } from "../models";
import { ServiceApi } from "../services/createServiceApi";
import { deviceService } from "../services/deviceService";
import { configureStore as configureStoreRedux } from "@reduxjs/toolkit";
import { deviceSliceReducer } from "@/store/slices/deviceSlice";
import { getStorageItemAsync } from "@/hooks/useStorageState";

export type ServiceApis = {
  device: ServiceApi<Device>;
};

export const serviceApis: ServiceApis = {
  device: deviceService,
};

export type ThunkExtraArgument = {
  serviceApis: ServiceApis;
  getSession: () => Promise<string | null>;
};

const getSession = async () => {
  // Retrieve token from storage directly
  const key = process.env.EXPO_PUBLIC_SESSION_STORAGE_KEY;
  if (!key) throw "Session storage key not found; cannot get session";
  return await getStorageItemAsync(key);
};

const extraArgument: ThunkExtraArgument = { serviceApis, getSession };

export const configureStore = () =>
  configureStoreRedux({
    reducer: {
      device: deviceSliceReducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        thunk: {
          extraArgument,
        },
      }),
  });
