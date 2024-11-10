import { Routine } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const routineService = createServiceApi<Routine>({
  resourceName: "routines",
});
