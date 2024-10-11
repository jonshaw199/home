import { Light } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const lightService = createServiceApi<Light>({
  baseUrl: `${base_url}/api/lights`,
});
