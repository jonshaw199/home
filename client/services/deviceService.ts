import { Device } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const deviceService = createServiceApi<Device>(
  `${base_url}/api/devices`
);
