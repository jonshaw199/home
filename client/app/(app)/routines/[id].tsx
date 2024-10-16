import ScreenWrapper from "@/components/lib/ScreenWrapper";
import RoutineDetails from "@/components/routines/routine/RoutineDetails";
import { useAppSelector } from "@/store";
import { Redirect, useLocalSearchParams } from "expo-router";
import React, { useMemo } from "react";

const RoutineDetailsScreen = () => {
  const { id } = useLocalSearchParams();
  const routines = useAppSelector((state) => state.routines.data);

  const routine = useMemo(() => {
    if (typeof id == "string" && id in routines) {
      return routines[id];
    }
  }, [id, routines]);

  if (!routine) {
    return <Redirect href="/" />;
  }

  return (
    <ScreenWrapper>
      <RoutineDetails routine={routine} />
    </ScreenWrapper>
  );
};

export default RoutineDetailsScreen;
