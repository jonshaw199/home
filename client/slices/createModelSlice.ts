import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { ID, Identifiable } from "@/models";
import { QueryParams } from "@/services/createServiceApi";
import { ServiceApis, ThunkExtraArgument } from "@/store/config";
import { Draft } from "immer";
import * as SecureStore from "expo-secure-store";

// Define the common slice state for each model
export interface ModelState<T extends Identifiable> {
  data: { [key: ID]: T };
  loading: boolean;
  error: string | null;
}

// Helper function to initialize model state
export function createInitialModelState<
  T extends Identifiable
>(): ModelState<T> {
  return {
    data: {},
    loading: false,
    error: null,
  };
}

// Generic function to create thunks and a slice for any model/resource
export function createModelSlice<T extends Identifiable>(
  name: string, // Name of the slice
  apiKey: keyof ServiceApis
) {
  // Thunks

  // Fetch all resources (GET /model)
  const fetchAll = createAsyncThunk<
    { [key: ID]: T },
    QueryParams | undefined,
    {
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/fetchAll`, async (queryParams, { extra }) => {
    const token = await extra.getSession(); // Retrieve the session token from extraArgument
    const api = extra.serviceApis[apiKey];
    return api.readAll({ token, queryParams });
  });

  // Fetch one resource by ID (GET /model/:id)
  const fetchOne = createAsyncThunk<
    T,
    ID,
    {
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/fetchOne`, async (id, { extra }) => {
    const token = await extra.getSession();
    const api = extra.serviceApis[apiKey];
    return api.readOne({ token, id });
  });

  // Create a new resource (POST /model)
  const createOne = createAsyncThunk<
    T,
    Partial<T>,
    {
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/createOne`, async (data, { extra }) => {
    const token = await extra.getSession();
    const api = extra.serviceApis[apiKey];
    return api.createOne({ token, data });
  });

  // Update a resource (PUT /model/:id)
  const updateOne = createAsyncThunk<
    T,
    { id: ID; data: Partial<T> },
    {
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/updateOne`, async ({ id, data }, { extra }) => {
    const token = await extra.getSession();
    const api = extra.serviceApis[apiKey];
    return api.updateOne({ token, id, data });
  });

  // Delete a resource (DELETE /model/:id)
  const deleteOne = createAsyncThunk<
    ID,
    ID,
    {
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/deleteOne`, async (id, { extra }) => {
    const token = await extra.getSession();
    const api = extra.serviceApis[apiKey];
    return api.deleteOne({ token, id });
  });

  // Create the slice
  const slice = createSlice({
    name,
    initialState: createInitialModelState<T>(),
    reducers: {},
    extraReducers: (builder) => {
      // Handle fetchAll
      builder.addCase(fetchAll.pending, (state) => {
        return { ...state, loading: true, error: null };
      });
      builder.addCase(
        fetchAll.fulfilled,
        (state, action: PayloadAction<{ [key: ID]: T }>) => {
          return { ...state, data: action.payload, loading: false };
        }
      );
      builder.addCase(fetchAll.rejected, (state, action) => {
        return {
          ...state,
          loading: false,
          error: action.error.message || "Failed to fetch data",
        };
      });

      // Handle fetchOne
      builder.addCase(fetchOne.pending, (state) => {
        return { ...state, loading: true, error: null };
      });
      builder.addCase(fetchOne.fulfilled, (state, { payload }) => {
        // Explicitly cast the payload as a Draft<T>
        // TODO: why is this necessary?
        const data = { ...state.data, [payload.id]: payload as Draft<T> };
        return { ...state, data, loading: false };
      });
      builder.addCase(fetchOne.rejected, (state, action) => {
        return {
          ...state,
          loading: false,
          error: action.error.message || "Failed to fetch resource",
        };
      });

      // Handle createOne
      builder.addCase(createOne.pending, (state) => {
        return { ...state, loading: true, error: null };
      });
      builder.addCase(createOne.fulfilled, (state, { payload }) => {
        // Explicitly cast the payload as a Draft<T>
        const data = { ...state.data, [payload.id]: payload as Draft<T> };
        return { ...state, data, loading: false };
      });
      builder.addCase(createOne.rejected, (state, action) => {
        return {
          ...state,
          loading: false,
          error: action.error.message || "Failed to create resource",
        };
      });

      // Handle updateOne
      builder.addCase(updateOne.pending, (state) => {
        return { ...state, loading: true, error: null };
      });
      builder.addCase(updateOne.fulfilled, (state, { payload }) => {
        // Explicitly cast the payload as a Draft<T>
        const data = { ...state.data, [payload.id]: payload as Draft<T> };
        return { ...state, data, loading: false };
      });
      builder.addCase(updateOne.rejected, (state, action) => {
        return {
          ...state,
          loading: false,
          error: action.error.message || "Failed to update resource",
        };
      });

      // Handle deleteOne
      builder.addCase(deleteOne.pending, (state) => {
        return { ...state, loading: true, error: null };
      });
      builder.addCase(
        deleteOne.fulfilled,
        (state, action: PayloadAction<ID>) => {
          const data = { ...state.data };
          delete data[action.payload];
          return { ...state, data, loading: false };
        }
      );
      builder.addCase(deleteOne.rejected, (state, action) => {
        return {
          ...state,
          loading: false,
          error: action.error.message || "Failed to delete resource",
        };
      });
    },
  });

  // Return the reducer and the thunks
  return {
    reducer: slice.reducer,
    actions: { fetchAll, fetchOne, createOne, updateOne, deleteOne },
  };
}
