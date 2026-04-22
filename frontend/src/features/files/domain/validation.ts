export function validateUploadInput(title: string, selectedFile: File | null): string | null {
  if (!title.trim() || !selectedFile) {
    return "Укажите название и выберите файл";
  }

  return null;
}

