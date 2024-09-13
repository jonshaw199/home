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
  DIAL,
  PC,
  SMART_PLUG,
}

export interface DeviceType extends Identifiable {
  name: string;
}

export interface Device extends Identifiable {
  deviceType: ID;
  location: ID;
  name: string;
}
