import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({ baseUrl: apiBaseUrl }),
  endpoints: (builder) => ({
    hamSandwichViz: builder.mutation({
      query: (data) => ({
        url: "ham-sandwich-viz/",
        method: "POST",
        body: data,
      }),
    }),
    teachHamSandwichViz: builder.mutation({
      query: (data) => ({
        url: "teach-ham-sandwich-viz/",
        method: "POST",
        body: data,
      }),
    }),
    getSampleFile: builder.query<
      { blob: Blob; fileType: string }, // Explicit return type
      string // fileType parameter is a string (csv, json, excel)
    >({
      query: (fileType) => `get-sample-file/${fileType}/`,
      transformResponse: async (response: Response, _meta, fileType) => {
        const blob = await response.blob();
        return { blob, fileType }; //  Explicitly return both blob & fileType
      },
    }),
  }),
});

export const {
  useHamSandwichVizMutation,
  useTeachHamSandwichVizMutation,
  useGetSampleFileQuery,
} = apiSlice;
