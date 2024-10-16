import { Routine } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const routineService = createServiceApi<Routine>({
  baseUrl: `${base_url}/api/routines`,
});
