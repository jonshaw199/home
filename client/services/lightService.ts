import { Light } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const lightService = createServiceApi<Light>({
  resourceName: "lights",
});
