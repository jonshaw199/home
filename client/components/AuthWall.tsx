import React, { useEffect, useState } from "react";
import { Text } from "react-native";
import { Redirect } from "expo-router";
import { useAppDispatch, useAppSelector } from "@/store";
import {
  loadFromStorage,
  selectIsLoading,
  selectIsSignedIn,
} from "@/store/slices/sessionSlice";

type AuthWallProps = {
  redirect: string;
  children: React.ReactNode;
};

export default function AuthWall({ redirect, children }: AuthWallProps) {
  const dispatch = useAppDispatch();

  const isSignedIn = useAppSelector(selectIsSignedIn);
  const isSigningIn = useAppSelector(selectIsLoading);

  const [isLoadingSessionFromStorage, setIsLoadingSessionFromStorage] =
    useState(true);

  useEffect(() => {
    // Load from storage
    dispatch(loadFromStorage()).then(() =>
      setIsLoadingSessionFromStorage(false)
    );
  }, [dispatch]);

  if (isSigningIn || isLoadingSessionFromStorage) {
    return <Text>Loading...</Text>;
  }

  if (!isSignedIn) {
    return <Redirect href={redirect} />;
  }

  return <>{children}</>;
}
