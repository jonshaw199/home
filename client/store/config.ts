import { Device, DeviceType, Plug } from "../models";
import { ServiceApi } from "../services/createServiceApi";
import { deviceService } from "../services/deviceService";
import {
  Reducer,
  configureStore as configureStoreRedux,
} from "@reduxjs/toolkit";
import { deviceSliceReducer } from "@/store/slices/deviceSlice";
import { getStorageItemAsync } from "@/hooks/useStorageState";
import { deviceTypeService } from "@/services/deviceTypeService";
import { deviceTypeSliceReducer } from "./slices/deviceTypeSlice";
import { plugService } from "@/services/plugService";
import { ModelState } from "./slices/createModelSlice";
import { plugSliceReducer } from "./slices/plugSlice";
import websocketMiddleware from "@/ws/websocketMiddleware";

/*
  Add new services to `ServiceApis` type and `serviceApis` object
*/
export type ServiceApis = {
  devices: ServiceApi<Device>;
  deviceTypes: ServiceApi<DeviceType>;
  plugs: ServiceApi<Plug>;
};

export const serviceApis: ServiceApis = {
  devices: deviceService,
  deviceTypes: deviceTypeService,
  plugs: plugService,
};

/*
  Add new slices to `RootReducer` type and `rootReducer` object
*/
type RootReducer = {
  devices: Reducer<ModelState<Device>>;
  deviceTypes: Reducer<ModelState<DeviceType>>;
  plugs: Reducer<ModelState<Plug>>;
};

const rootReducer: RootReducer = {
  devices: deviceSliceReducer,
  deviceTypes: deviceTypeSliceReducer,
  plugs: plugSliceReducer,
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
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        thunk: {
          extraArgument,
        },
      }).concat(websocketMiddleware),
  });
