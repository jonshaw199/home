import { Plug } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const plugService = createServiceApi<Plug>({
  resourceName: "plugs",
});
