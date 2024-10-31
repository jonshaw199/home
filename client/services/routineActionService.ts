import { RoutineAction } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const routineActionService = createServiceApi<RoutineAction>({
  resourceName: "actions",
});
