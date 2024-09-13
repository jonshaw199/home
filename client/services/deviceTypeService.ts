import { DeviceType } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const deviceTypeService = createServiceApi<DeviceType>({
  baseUrl: `${base_url}/api/device_types`,
});
