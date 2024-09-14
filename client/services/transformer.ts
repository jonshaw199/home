// Helper function to convert snake_case to camelCase

function transformObjOrArray(data: any, transformer: (obj: any) => any) {
  if (Array.isArray(data)) {
    return data.map((item) => transformer(item));
  } else if (data !== null && typeof data === "object") {
    return transformer(data);
  } else {
    return data;
  }
}

function snakeToCamel(snakeStr: string): string {
  return snakeStr.replace(/(_\w)/g, (matches) => matches[1].toUpperCase());
}

// Recursively convert keys from snake_case to camelCase
function convertKeysToCamelCase(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamelCase(item));
  } else if (obj !== null && typeof obj === "object") {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      const camelKey = snakeToCamel(key);
      acc[camelKey] = convertKeysToCamelCase(value);
      return acc;
    }, {} as any);
  }
  return obj; // Return the value as is if it's not an object or array
}

function convertUuidToId(obj: any): any {
  if ("uuid" in obj) {
    const newObj = { ...obj, id: obj.uuid };
    delete newObj.uuid;
    return newObj;
  }
  return obj;
}

export default function transform({
  data,
  customTransformer = (obj) => obj,
}: {
  data: any;
  customTransformer?: (obj: any) => any;
}): any {
  try {
    // snake case -> camel case
    let transformed = transformObjOrArray(data, convertKeysToCamelCase);
    // uuid -> id
    transformed = transformObjOrArray(transformed, convertUuidToId);
    // custom transformations by consumers
    return transformObjOrArray(transformed, customTransformer);
  } catch (e) {
    throw e;
  }
}
