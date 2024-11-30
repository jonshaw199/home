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

const getAuthHeaders = ({ token }: { token?: string | null }) => ({
  Authorization: `Token ${token}`,
});

export type ServiceApi<T extends Identifiable> = {
  createOne: ({
    baseUrl,
    token,
    data,
  }: {
    baseUrl: string;
    token?: string | null;
    data: Partial<T>;
  }) => Promise<T>;
  createMany: ({
    baseUrl,
    token,
    data,
  }: {
    baseUrl: string;
    token?: string | null;
    data: Partial<T>[];
  }) => Promise<{ [key: ID]: T }>;
  readOne: ({
    baseUrl,
    token,
    id,
  }: {
    baseUrl: string;
    token: string | null;
    id: ID;
  }) => Promise<T>;
  readAll: ({
    baseUrl,
    token,
    queryParams,
  }: {
    baseUrl: string;
    token?: string | null;
    queryParams?: QueryParams;
  }) => Promise<{ [key: ID]: T }>;
  updateOne: ({
    baseUrl,
    token,
    id,
    data,
  }: {
    baseUrl: string;
    token?: string | null;
    id: ID;
    data: Partial<T>;
  }) => Promise<T>;
  updateMany: ({
    baseUrl,
    token,
    data,
  }: {
    baseUrl: string;
    token?: string | null;
    data: { id: ID; payload: Partial<T> }[];
  }) => Promise<{ [key: ID]: T }>;
  deleteOne: ({
    baseUrl,
    token,
    id,
  }: {
    baseUrl: string;
    token?: string | null;
    id: ID;
  }) => Promise<ID>;
  deleteMany: ({
    baseUrl,
    token,
    ids,
  }: {
    baseUrl: string;
    token?: string | null;
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
  resourceName,
  transformer: customTransformer = (obj) => obj,
}: {
  resourceName: string;
  transformer?: (obj: T) => T;
}): ServiceApi<T> {
  return {
    async createOne({ baseUrl, token, data }) {
      return fetchAndTransform<T>({
        url: `${baseUrl}/${resourceName}`,
        options: {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders({ token }),
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
    },

    async createMany({ baseUrl, token, data }) {
      const results = await fetchAndTransform<T[]>({
        url: `${baseUrl}/${resourceName}`,
        options: {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders({ token }),
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
      return keyById<T>(results);
    },

    async readOne({ baseUrl, token, id }) {
      return fetchAndTransform<T>({
        url: `${baseUrl}/${resourceName}/${id}`,
        options: {
          method: "GET",
          headers: getAuthHeaders({ token }),
        },
        customTransformer,
      });
    },

    async readAll({ baseUrl, token, queryParams }) {
      const queryString = buildQueryString(queryParams);
      const results = await fetchAndTransform<T[]>({
        url: `${baseUrl}/${resourceName}${queryString}`,
        options: {
          method: "GET",
          headers: getAuthHeaders({ token }),
        },
        customTransformer,
      });
      return keyById<T>(results);
    },

    async updateOne({ baseUrl, token, id, data }) {
      return fetchAndTransform<T>({
        url: `${baseUrl}/${resourceName}/${id}`,
        options: {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders({ token }),
          },
          body: JSON.stringify(data),
        },
        customTransformer,
      });
    },

    async updateMany({ baseUrl, token, data }) {
      const promises = data.map(({ id, payload }) =>
        fetchAndTransform<T>({
          url: `${baseUrl}/${resourceName}/${id}`,
          options: {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              ...getAuthHeaders({ token }),
            },
            body: JSON.stringify(payload),
          },
          customTransformer,
        })
      );
      const results = await Promise.all(promises);
      return keyById<T>(results);
    },

    async deleteOne({ baseUrl, token, id }) {
      const response = await fetch(`${baseUrl}/${resourceName}/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders({ token }),
      });
      if (!response.ok) {
        throw new Error(`Failed to delete resource: ${response.statusText}`);
      }
      return id;
    },

    async deleteMany({ baseUrl, token, ids }) {
      const promises = ids.map((id) =>
        fetch(`${baseUrl}/${resourceName}/${id}`, {
          method: "DELETE",
          headers: getAuthHeaders({ token }),
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
