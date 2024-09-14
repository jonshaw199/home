import { Plug } from "@/models";
import { createServiceApi } from "./createServiceApi";

const base_url = process.env.EXPO_PUBLIC_HOME_API_URL;

export const plugService = createServiceApi<Plug>({
  baseUrl: `${base_url}/api/plugs`,
});
