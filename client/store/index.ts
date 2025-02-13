import { UnknownAction } from "redux";
import { ThunkAction } from "redux-thunk";
import { configureStore } from "./config";
import { useDispatch } from "react-redux";
import { useSelector } from "react-redux";
import { useStore } from "react-redux";

export const store = configureStore();

// Get the type of our store variable
export type AppStore = typeof store;
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<AppStore["getState"]>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = AppStore["dispatch"];

/*
  Note that this assumes that there is no meaningful 
  return value from the thunk. If your thunk returns 
  a promise and you want to use the returned promise 
  after dispatching the thunk, you'd want to use this 
  as AppThunk<Promise<SomeReturnType>>.
*/
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  UnknownAction
>;

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
