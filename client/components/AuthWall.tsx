import React, { useEffect, useState } from "react";
import { Text } from "react-native";
import { Redirect } from "expo-router";
import { useAppDispatch, useAppSelector } from "@/store";
import {
  loadFromStorage,
  selectIsLoading,
  selectSession,
} from "@/store/slices/sessionSlice";

type AuthWallProps = {
  redirect: string;
  children: React.ReactNode;
};

export default function AuthWall({ redirect, children }: AuthWallProps) {
  const dispatch = useAppDispatch();

  const session = useAppSelector(selectSession);
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

  if (!session) {
    return <Redirect href={redirect} />;
  }

  return <>{children}</>;
}
