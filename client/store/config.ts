import { Device, DeviceType, Environmental, Plug } from "../models";
import { ServiceApi } from "../services/createServiceApi";
import { deviceService } from "../services/deviceService";
import {
  Reducer,
  configureStore as configureStoreRedux,
} from "@reduxjs/toolkit";
import { deviceSliceReducer } from "@/store/slices/deviceSlice";
import { deviceTypeService } from "@/services/deviceTypeService";
import { deviceTypeSliceReducer } from "./slices/deviceTypeSlice";
import { plugService } from "@/services/plugService";
import { ModelState } from "./slices/createModelSlice";
import { plugSliceReducer } from "./slices/plugSlice";
import websocketMiddleware from "@/ws/websocketMiddleware";
import { environmentalService } from "@/services/environmentalService";
import { environmentalSliceReducer } from "./slices/environmentalSlice";
import { SessionState, sessionSliceReducer } from "./slices/sessionSlice";
import { getStorageItemAsync } from "@/hooks/useStorageState";

const storageKey = process.env.EXPO_PUBLIC_SESSION_STORAGE_KEY;
if (!storageKey) throw "EXPO_PUBLIC_SESSION_STORAGE_KEY must be defined";

/*
  Add new services to `ServiceApis` type and `serviceApis` object
*/
export type ServiceApis = {
  devices: ServiceApi<Device>;
  deviceTypes: ServiceApi<DeviceType>;
  plugs: ServiceApi<Plug>;
  environmentals: ServiceApi<Environmental>;
};

export const serviceApis: ServiceApis = {
  devices: deviceService,
  deviceTypes: deviceTypeService,
  plugs: plugService,
  environmentals: environmentalService,
};

/*
  Add new slices to `RootReducer` type and `rootReducer` object
*/
type RootReducer = {
  devices: Reducer<ModelState<Device>>;
  deviceTypes: Reducer<ModelState<DeviceType>>;
  plugs: Reducer<ModelState<Plug>>;
  environmentals: Reducer<ModelState<Environmental>>;
  session: Reducer<SessionState>;
};

const rootReducer: RootReducer = {
  devices: deviceSliceReducer,
  deviceTypes: deviceTypeSliceReducer,
  plugs: plugSliceReducer,
  environmentals: environmentalSliceReducer,
  session: sessionSliceReducer,
};

export type ThunkExtraArgument = {
  serviceApis: ServiceApis;
  getSession: () => Promise<string | null>;
};

const extraArgument: ThunkExtraArgument = {
  serviceApis,
  getSession: () => getStorageItemAsync(storageKey),
};

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
