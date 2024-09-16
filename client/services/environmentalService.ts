import { Environmental } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const environmentalService = createServiceApi<Environmental>({
  baseUrl: `${base_url}/api/environmentals`,
});
