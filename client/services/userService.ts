import { User } from "@/models";
import { createServiceApi } from "./createServiceApi";

export const userService = createServiceApi<User>({ baseUrl: "/api/users" });
