import { ID, Identifiable } from "@/models";
import transform from "./transformer";

export type QueryParams = Record<string, string | number | boolean>;

/*
export type PaginatedResponse<T extends Identifiable> = {
  results: { [key: ID]: T };
  count: number;
  next: string | null;
  previous: string | null;
};
*/

export type ServiceApi<T extends Identifiable> = {
  createOne: ({
    token,
    data,
  }: {
    token: string | null;
    data: Partial<T>;
  }) => Promise<T>;
  createMany: ({
    token,
    data,
  }: {
    token: string | null;
    data: Partial<T>[];
  }) => Promise<{ [key: ID]: T }>;
  readOne: ({ token, id }: { token: string | null; id: ID }) => Promise<T>;
  readAll: ({
    token,
    queryParams,
  }: {
    token: string | null;
    queryParams?: QueryParams;
  }) => Promise<{ [key: ID]: T }>;
  updateOne: ({
    token,
    data,
  }: {
    token: string | null;
    id: ID;
    data: Partial<T>;
  }) => Promise<T>;
  updateMany: ({
    token,
    data,
  }: {
    token: string | null;
    data: { id: ID; payload: Partial<T> }[];
  }) => Promise<{ [key: ID]: T }>;
  deleteOne: ({ token, id }: { token: string | null; id: ID }) => Promise<ID>;
  deleteMany: ({
    token,
    ids,
  }: {
    token: string | null;
    ids: ID[];
  }) => Promise<void>;
};

function buildQueryString(params?: QueryParams): string {
  if (!params) return "";
  return (
    "?" +
    Object.entries(params)
      .map(
        ([key, value]) =>
          `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
      )
      .join("&")
  );
}

function keyById<T extends Identifiable>(arr: T[]) {
  return arr.reduce((res: { [key: ID]: T }, cur: T) => {
    res[cur.id] = cur;
    return res;
  }, {});
}

// Utility function to handle fetch and camelCase conversion
async function fetchAndTransform<T>({
  url,
  options,
  customTransformer = (obj) => obj,
}: {
  url: string;
  options: RequestInit;
  customTransformer?: (obj: any) => any;
}): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Failed to fetch resource: ${response.statusText}`);
  }
  const data = await response.json();

  // Transform data
  return transform({ data, customTransformer });
}

export function createServiceApi<T extends Identifiable>({
  baseUrl,
  transformer: customTransformer = (obj) => obj,
}: {
  baseUrl: string;
  transformer?: (obj: T) => T;
}): ServiceApi<T> {
  return {
    async createOne({ token, data }) {
      return fetchAndTransform<T>({
        url: baseUrl,
        options: {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
    },

    async createMany({ token, data }) {
      const results = await fetchAndTransform<T[]>({
        url: baseUrl,
        options: {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
      return keyById<T>(results);
    },

    async readOne({ token, id }) {
      return fetchAndTransform<T>({
        url: `${baseUrl}/${id}`,
        options: {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
        customTransformer,
      });
    },

    async readAll({ token, queryParams }) {
      const queryString = buildQueryString(queryParams);
      const results = await fetchAndTransform<T[]>({
        url: `${baseUrl}${queryString}`,
        options: {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
        customTransformer,
      });
      return keyById<T>(results);
    },

    async updateOne({ token, id, data }) {
      return fetchAndTransform<T>({
        url: `${baseUrl}/${id}`,
        options: {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
    },

    async updateMany({ token, data }) {
      const promises = data.map(({ id, payload }) =>
        fetchAndTransform<T>({
          url: `${baseUrl}/${id}`,
          options: {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
          },
          customTransformer,
        })
      );
      const results = await Promise.all(promises);
      return keyById<T>(results);
    },

    async deleteOne({ token, id }) {
      const response = await fetch(`${baseUrl}/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to delete resource: ${response.statusText}`);
      }
      return id;
    },

    async deleteMany({ token, ids }) {
      const promises = ids.map((id) =>
        fetch(`${baseUrl}/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          if (!response.ok) {
            throw new Error(
              `Failed to delete resource ${id}: ${response.statusText}`
            );
          }
        })
      );
      await Promise.all(promises);
    },
  };
}
