import { AlertItem } from "../domain/types";
import { API_BASE_URL } from "../../../shared/api/config";

export async function fetchAlerts(): Promise<AlertItem[]> {
  const response = await fetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Не удалось загрузить данные");
  }

  return response.json() as Promise<AlertItem[]>;
}

