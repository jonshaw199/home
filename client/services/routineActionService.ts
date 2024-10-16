import { RoutineAction } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const routineActionService = createServiceApi<RoutineAction>({
  baseUrl: `${base_url}/api/actions`,
});
