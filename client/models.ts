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

export interface Device extends Identifiable {
  name: string;
}