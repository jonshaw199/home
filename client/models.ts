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
  PC = "7d69fa8c-c969-427d-836f-f45523e5dbb5",
  PLUG = "f8773a6b-f0f0-489c-aa0a-fca087020069",
  ENVIRONMENTAL = "973f049b-64dc-442c-838e-b7fae7270fe2",
}

export interface DeviceType extends Identifiable {
  name: string;
}

export interface Device extends Identifiable {
  deviceType: ID;
  location: ID;
  name: string;
  lastStatusUpdate?: string | null;
  plug?: ID | null;
  system?: ID | null;
  environmental?: ID | null;
}

export interface Plug extends Identifiable {
  isOn: boolean;
}

export interface Environmental extends Identifiable {
  humidity?: number | null;
  temperatureC?: number | null;
  temperatureF?: number | null;
}
