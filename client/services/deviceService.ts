import { Device } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const deviceService = createServiceApi<Device>({
  resourceName: "devices",
});
