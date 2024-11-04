import {
  createSlice,
  createAsyncThunk,
  PayloadAction,
  ActionReducerMapBuilder,
} from "@reduxjs/toolkit";
import { ID, Identifiable } from "@/models";
import { QueryParams } from "@/services/createServiceApi";
import { ServiceApis, ThunkExtraArgument } from "@/store/config";
import { Draft } from "immer";
import { RootState } from "@/store/index";
import { selectApiUrl } from "./urlSlice";

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
  apiKey: keyof ServiceApis,
  extraReducers?: (builder: ActionReducerMapBuilder<ModelState<T>>) => void
) {
  // Thunks

  // Fetch all resources (GET /model)
  const fetchAll = createAsyncThunk<
    { [key: ID]: T },
    QueryParams | undefined,
    {
      state: RootState;
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/fetchAll`, async (queryParams, { getState, extra }) => {
    const { session } = getState();
    const url = selectApiUrl(getState());
    if (!url) throw "URL not defined; unable to make request";
    const api = extra.serviceApis[apiKey];
    return api.readAll({
      baseUrl: url,
      token: session.data.token,
      queryParams,
    });
  });

  // Fetch one resource by ID (GET /model/:id)
  const fetchOne = createAsyncThunk<
    T,
    ID,
    {
      state: RootState;
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/fetchOne`, async (id, { getState, extra }) => {
    const { session } = getState();
    const url = selectApiUrl(getState());
    if (!url) throw "URL not defined; unable to make request";
    const api = extra.serviceApis[apiKey];
    return api.readOne({ baseUrl: url, token: session.session, id });
  });

  // Create a new resource (POST /model)
  const createOne = createAsyncThunk<
    T,
    Partial<T>,
    {
      state: RootState;
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/createOne`, async (data, { getState, extra }) => {
    const { session } = getState();
    const url = selectApiUrl(getState());
    if (!url) throw "URL not defined; unable to make request";
    const api = extra.serviceApis[apiKey];
    return api.createOne({
      baseUrl: url,
      token: session.data.token,
      data,
    });
  });

  // Update a resource (PUT /model/:id)
  const updateOne = createAsyncThunk<
    T,
    { id: ID; data: Partial<T> },
    {
      state: RootState;
      extra: ThunkExtraArgument;
    }
    // @ts-ignore
  >(`${name}/updateOne`, async ({ id, data }, { getState, extra }) => {
    const { session } = getState();
    const url = selectApiUrl(getState());
    if (!url) throw "URL not defined; unable to make request";
    const api = extra.serviceApis[apiKey];
    return api.updateOne({
      baseUrl: url,
      token: session.data.token,
      id,
      data,
    });
  });

  // Delete a resource (DELETE /model/:id)
  const deleteOne = createAsyncThunk<
    ID,
    ID,
    {
      state: RootState;
      extra: ThunkExtraArgument;
    }
  >(`${name}/deleteOne`, async (id, { getState, extra }) => {
    const { session } = getState();
    const url = selectApiUrl(getState());
    if (!url) throw "URL not defined; unable to make request";
    const api = extra.serviceApis[apiKey];
    return api.deleteOne({ baseUrl: url, token: session.data.token, id });
  });

  // Create the slice
  const slice = createSlice({
    name,
    initialState: createInitialModelState<T>(),
    reducers: {
      // Action to update a single resource
      updateResource: (state, action: PayloadAction<T>) => {
        const resource = action.payload;
        const data = { ...state.data, [resource.id]: resource as Draft<T> };
        return { ...state, data };
      },
      // Action to set multiple resources
      setResources: (state, action: PayloadAction<{ [key: ID]: T }>) => {
        return { ...state, data: action.payload };
      },
      // Additional action to handle specific update scenarios
      updateResourceField: (
        state,
        action: PayloadAction<{ id: ID; field: keyof T; value: any }>
      ) => {
        const { id, field, value } = action.payload;
        const resource = state.data[id];
        if (resource) {
          const updated = { ...resource, [field]: value };
          const data = { ...state.data, [resource.id]: updated };
          return { ...state, data };
        }
      },
    },
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

      if (extraReducers) {
        extraReducers(builder);
      }
    },
  });

  // Return the reducer and the thunks
  return {
    reducer: slice.reducer,
    actions: {
      ...slice.actions,
      fetchAll,
      fetchOne,
      createOne,
      updateOne,
      deleteOne,
    },
  };
}
