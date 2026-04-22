import { FormEvent, useEffect, useState } from "react";

import { fetchAlerts } from "../../alerts/data/alertsApi";
import { AlertItem } from "../../alerts/domain/types";
import { fetchFiles, uploadFile } from "../../files/data/filesApi";
import { validateUploadInput } from "../../files/domain/validation";
import { FileItem } from "../../files/domain/types";

export function useDashboardPage() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([fetchFiles(), fetchAlerts()]);
      setFiles(filesData);
      setAlerts(alertsData);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validateUploadInput(title, selectedFile);
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await uploadFile(title.trim(), selectedFile);
      setShowModal(false);
      setTitle("");
      setSelectedFile(null);
      await loadData();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    files,
    alerts,
    isLoading,
    isSubmitting,
    showModal,
    title,
    errorMessage,
    setShowModal,
    setTitle,
    setSelectedFile,
    loadData,
    handleSubmit,
  };
}

