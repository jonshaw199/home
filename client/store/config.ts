import { Device, DeviceType } from "../models";
import { ServiceApi } from "../services/createServiceApi";
import { deviceService } from "../services/deviceService";
import { configureStore as configureStoreRedux } from "@reduxjs/toolkit";
import { deviceSliceReducer } from "@/store/slices/deviceSlice";
import { getStorageItemAsync } from "@/hooks/useStorageState";
import { deviceTypeService } from "@/services/deviceTypeService";
import { deviceTypeSliceReducer } from "./slices/deviceTypeSlice";

export type ServiceApis = {
  devices: ServiceApi<Device>;
  deviceTypes: ServiceApi<DeviceType>;
};

export const serviceApis: ServiceApis = {
  devices: deviceService,
  deviceTypes: deviceTypeService,
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
      devices: deviceSliceReducer,
      deviceTypes: deviceTypeSliceReducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        thunk: {
          extraArgument,
        },
      }),
  });
