import DeviceDetails from "@/components/devices/device/DeviceDetails";
import ScreenWrapper from "@/components/lib/ScreenWrapper";
import { useAppSelector } from "@/store";
import { Redirect, useLocalSearchParams } from "expo-router";
import React, { useMemo } from "react";

const DeviceDetailsScreen = () => {
  const { id } = useLocalSearchParams();
  const devices = useAppSelector((state) => state.devices.data);

  const device = useMemo(() => {
    if (typeof id == "string" && id in devices) {
      return devices[id];
    }
  }, [id, devices]);

  if (!device) {
    return <Redirect href="/" />;
  }

  return (
    <ScreenWrapper>
      <DeviceDetails device={device} />
    </ScreenWrapper>
  );
};

export default DeviceDetailsScreen;
