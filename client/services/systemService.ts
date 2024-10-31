import { System } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const systemService = createServiceApi<System>({
  resourceName: "systems",
});
