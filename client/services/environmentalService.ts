import { Environmental } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const environmentalService = createServiceApi<Environmental>({
  resourceName: "environmentals",
});
