export const getToken = async ({
  username,
  password,
  url,
}: {
  username: string;
  password: string;
  url: string;
}): Promise<{ token?: string; profile?: string }> => {
  const response = await fetch(`${url}/api-token-auth/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username,
      password,
    }),
  });
  const json = await response.json();
  return {
    token: json?.token,
    profile: json?.profile,
  };
};

export const validateToken = async (token?: string) => {
  // TODO
  return true;
};
