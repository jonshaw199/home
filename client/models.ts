export type ID = string | number;

export type Nullable<T> = T | null | undefined;

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
  lastStatusUpdate: Nullable<string>;
  vendorId: Nullable<ID>;
  plug: Nullable<ID>;
  system: Nullable<ID>;
  environmental: Nullable<ID>;
  light: Nullable<ID>;
}

export interface Plug extends Identifiable {
  isOn: boolean;
  device: ID;
}

export interface Environmental extends Identifiable {
  humidity: Nullable<number>;
  temperatureC: Nullable<number>;
  temperatureF: Nullable<number>;
  device: ID;
}

export interface System extends Identifiable {
  cpuUsage: Nullable<number>;
  memUsage: Nullable<number>;
  device: ID;
}

export interface Light extends Identifiable {
  isOn: Nullable<boolean>;
  brightness: Nullable<number>;
  color: Nullable<string>;
}

export enum ActionType {
  STATUS_SYSTEM = "system__status",
  STATUS_ENVIRONMENTAL = "environmental__status",
  STATUS_PLUG = "plug__status",
  STATUS_LIGHT = "light__status",
}

export interface Routine extends Identifiable {
  name: string;
  active: boolean;
  triggers: Nullable<string>;
  repeatInterval: Nullable<string>;
  evalCondition: Nullable<string>;
  actions: Nullable<ID[]>;
  location: ID;
}

export interface RoutineAction extends Identifiable {
  name: string;
  active: boolean;
  routine: ID;
  type: ActionType;
  evalParams: Nullable<string>;
}
