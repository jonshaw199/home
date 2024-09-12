import { ID, Identifiable } from "@/models";

export type QueryParams = Record<string, string | number | boolean>;

export type PaginatedResponse<T extends Identifiable> = {
  results: { [key: ID]: T };
  count: number;
  next: string | null;
  previous: string | null;
};

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
  }) => Promise<PaginatedResponse<T>>;
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

export function createServiceApi<T extends Identifiable>(
  baseUrl: string
): ServiceApi<T> {
  return {
    async createOne({ token, data }) {
      const response = await fetch(baseUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`Failed to create resource: ${response.statusText}`);
      }
      return response.json();
    },

    async createMany({ token, data }) {
      const response = await fetch(baseUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`Failed to create resources: ${response.statusText}`);
      }
      const results = await response.json();
      return keyById<T>(results);
    },

    async readOne({ token, id }) {
      const response = await fetch(`${baseUrl}/${id}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch resource: ${response.statusText}`);
      }
      return response.json();
    },

    async readAll({ token, queryParams }) {
      const queryString = buildQueryString(queryParams);
      const response = await fetch(`${baseUrl}${queryString}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch resources: ${response.statusText}`);
      }
      const results = await response.json();
      return keyById<T>(results);
    },

    async updateOne({ token, id, data }) {
      const response = await fetch(`${baseUrl}/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`Failed to update resource: ${response.statusText}`);
      }
      return response.json();
    },

    async updateMany({ token, data }) {
      const promises = data.map(({ id, payload }) =>
        fetch(`${baseUrl}/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }).then(async (response) => {
          if (!response.ok) {
            throw new Error(
              `Failed to update resource ${id}: ${response.statusText}`
            );
          }
          return response.json();
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
