import { ID, Identifiable } from "@/models";

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

// Helper function to convert snake_case to camelCase
function snakeToCamel(snakeStr: string): string {
  return snakeStr.replace(/(_\w)/g, (matches) => matches[1].toUpperCase());
}

// Recursively convert keys from snake_case to camelCase
function convertKeysToCamelCase(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamelCase(item));
  } else if (obj !== null && typeof obj === "object") {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      const camelKey = snakeToCamel(key);
      acc[camelKey] = convertKeysToCamelCase(value);
      return acc;
    }, {} as any);
  }
  return obj; // Return the value as is if it's not an object or array
}

// Utility function to handle fetch and camelCase conversion
async function fetchAndConvert<T>(
  url: string,
  options: RequestInit
): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Failed to fetch resource: ${response.statusText}`);
  }
  const data = await response.json();
  return convertKeysToCamelCase(data);
}

export function createServiceApi<T extends Identifiable>(
  baseUrl: string
): ServiceApi<T> {
  return {
    async createOne({ token, data }) {
      return fetchAndConvert<T>(baseUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
    },

    async createMany({ token, data }) {
      const results = await fetchAndConvert<T[]>(baseUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      return keyById<T>(results);
    },

    async readOne({ token, id }) {
      return fetchAndConvert<T>(`${baseUrl}/${id}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    },

    async readAll({ token, queryParams }) {
      const queryString = buildQueryString(queryParams);
      const results = await fetchAndConvert<T[]>(`${baseUrl}${queryString}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return keyById<T>(results);
    },

    async updateOne({ token, id, data }) {
      return fetchAndConvert<T>(`${baseUrl}/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
    },

    async updateMany({ token, data }) {
      const promises = data.map(({ id, payload }) =>
        fetchAndConvert<T>(`${baseUrl}/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
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
