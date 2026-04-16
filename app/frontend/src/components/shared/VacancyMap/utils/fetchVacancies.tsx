export interface FetchVacancyConfig {
  baseUrl: string;
  params: Record<string, string>;
  headers?: HeadersInit;
  parseResponse: (data: Record<string, number>) => number;
}


export default async function fetchVacancies(
  regionName: string,
  configs: readonly FetchVacancyConfig[],
  signal: AbortSignal,
): Promise<number> {
  const results = await Promise.allSettled(
    configs.map(async (cfg) => {
      const params = new URLSearchParams({ ...cfg.params });
      const response = await fetch(`${cfg.baseUrl}?${params}`, {
        headers: cfg.headers,
        signal,
      });

      if (response.status === 429) {
        const retryAfter = Number(response.headers.get('Retry-After') || 1);
        await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
        return fetchVacancies(regionName, [cfg], signal);
      }

      if (!response.ok) return 0;
      return cfg.parseResponse(await response.json());
    }),
  );

  return results.reduce(
    (sum, result) => sum + (result.status === 'fulfilled' ? result.value : 0),
    0,
  );
}