import {
  Device,
  DeviceType,
  Environmental,
  Light,
  Plug,
  Routine,
  RoutineAction,
  System,
} from "../models";
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
import { systemService } from "@/services/systemService";
import { systemSliceReducer } from "./slices/systemSlice";
import { lightService } from "@/services/lightService";
import { lightSliceReducer } from "./slices/lightSlice";
import { routineService } from "@/services/routineService";
import { routineActionService } from "@/services/routineActionService";
import { routineSliceReducer } from "./slices/routineSlice";
import { routineActionSliceReducer } from "./slices/routineActionSlice";
import { urlSliceReducer, UrlState } from "./slices/urlSlice";

/*
  Add new services to `ServiceApis` type and `serviceApis` object
*/
export type ServiceApis = {
  devices: ServiceApi<Device>;
  deviceTypes: ServiceApi<DeviceType>;
  plugs: ServiceApi<Plug>;
  environmentals: ServiceApi<Environmental>;
  systems: ServiceApi<System>;
  lights: ServiceApi<Light>;
  routines: ServiceApi<Routine>;
  routineActions: ServiceApi<RoutineAction>;
};

export const serviceApis: ServiceApis = {
  devices: deviceService,
  deviceTypes: deviceTypeService,
  plugs: plugService,
  environmentals: environmentalService,
  systems: systemService,
  lights: lightService,
  routines: routineService,
  routineActions: routineActionService,
};

/*
  Add new slices to `RootReducer` type and `rootReducer` object
*/
type RootReducer = {
  devices: Reducer<ModelState<Device>>;
  deviceTypes: Reducer<ModelState<DeviceType>>;
  plugs: Reducer<ModelState<Plug>>;
  environmentals: Reducer<ModelState<Environmental>>;
  systems: Reducer<ModelState<System>>;
  lights: Reducer<ModelState<Light>>;
  session: Reducer<SessionState>;
  url: Reducer<UrlState>;
  routines: Reducer<ModelState<Routine>>;
  routineActions: Reducer<ModelState<RoutineAction>>;
};

const rootReducer: RootReducer = {
  devices: deviceSliceReducer,
  deviceTypes: deviceTypeSliceReducer,
  plugs: plugSliceReducer,
  environmentals: environmentalSliceReducer,
  systems: systemSliceReducer,
  lights: lightSliceReducer,
  session: sessionSliceReducer,
  url: urlSliceReducer,
  routines: routineSliceReducer,
  routineActions: routineActionSliceReducer,
};

export type ThunkExtraArgument = {
  serviceApis: ServiceApis;
};

const extraArgument: ThunkExtraArgument = {
  serviceApis,
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
