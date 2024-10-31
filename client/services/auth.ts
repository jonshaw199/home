export const getToken = async ({
  username,
  password,
  url,
}: {
  username: string;
  password: string;
  url: string;
}) => {
  const response = await fetch(`${url}/api-token-auth/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      password,
    }),
  });
  const json = await response.json();
  const token = json?.token;
  if (!token) {
    throw "Failed to get auth token";
  }
  return token;
};

export const validateToken = async (token: string) => {
  // TODO
  return true;
};
