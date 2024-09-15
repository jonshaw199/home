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
  DIAL = "18014960-6d98-412c-a62d-e400c647112e",
  PC = "380d7a59-f957-41f3-9d51-def726b9e52a",
  PLUG = "cf7d8486-18ad-4064-b757-e671a4749a3e",
}

export interface DeviceType extends Identifiable {
  name: string;
}

export interface Device extends Identifiable {
  deviceType: ID;
  location: ID;
  name: string;
  plug?: ID;
  system?: ID;
}

export interface Plug extends Identifiable {
  isOn: boolean;
}
