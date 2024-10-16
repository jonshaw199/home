export type ID = string | number;

// Base interface with an id property
export interface Identifiable {
  id: ID;
}

// Extend this in your model interfaces
export interface User extends Identifiable {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
}

export enum DeviceTypes {
  DIAL = "Dial",
  PC = "PC",
  PLUG = "Plug",
  ENVIRONMENTAL = "Environmental",
  LIGHT = "Light",
}

export interface DeviceType extends Identifiable {
  name: string;
}

export interface Device extends Identifiable {
  deviceType: ID;
  location: ID;
  name: string;
  lastStatusUpdate?: string;
  plug?: ID;
  system?: ID;
  environmental?: ID;
  light?: ID;
}

export interface Plug extends Identifiable {
  isOn: boolean;
  device?: ID;
}

export interface Environmental extends Identifiable {
  humidity?: number;
  temperatureC?: number;
  temperatureF?: number;
  device?: ID;
}

export interface System extends Identifiable {
  cpuUsage?: number;
  memUsage?: number;
  device?: ID;
}

export interface Light extends Identifiable {
  isOn?: boolean;
  brightness?: number;
  color?: string;
}

export enum Action {
  STATUS_SYSTEM = "system__status",
  STATUS_ENVIRONMENTAL = "environmental__status",
  STATUS_PLUG = "plug__status",
  STATUS_LIGHT = "light__status",
}
