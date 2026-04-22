import { FileItem } from "../domain/types";
import { API_BASE_URL } from "../../../shared/api/config";

export async function fetchFiles(): Promise<FileItem[]> {
  const response = await fetch(`${API_BASE_URL}/files`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Не удалось загрузить данные");
  }

  return response.json() as Promise<FileItem[]>;
}

export async function uploadFile(title: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/files`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Не удалось загрузить файл");
  }
}

export function getFileDownloadUrl(fileId: string): string {
  return `${API_BASE_URL}/files/${fileId}/download`;
}

