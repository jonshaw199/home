import React from "react";
import { Text } from "react-native";
import { useSession } from "@/context/SessionContext";
import { Redirect } from "expo-router";

type AuthWallProps = {
  redirect: string;
  children: React.ReactNode;
};

export default function AuthWall({ redirect, children }: AuthWallProps) {
  const { session, isLoading } = useSession();

  if (isLoading) {
    return <Text>Loading...</Text>;
  }

  if (!session) {
    return <Redirect href={redirect} />;
  }

  return <>{children}</>;
}
