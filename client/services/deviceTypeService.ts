import { DeviceType } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const deviceTypeService = createServiceApi<DeviceType>({
  resourceName: "device_types",
});
