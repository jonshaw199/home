import { System } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const systemService = createServiceApi<System>({
  baseUrl: `${base_url}/api/systems`,
});
