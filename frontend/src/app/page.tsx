"use client";

import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Container,
  Row,
} from "react-bootstrap";
import { AlertsTable } from "../features/alerts/ui/AlertsTable";
import { useDashboardPage } from "../features/dashboard/ui/useDashboardPage";
import { FilesTable } from "../features/files/ui/FilesTable";
import { UploadFileModal } from "../features/files/ui/UploadFileModal";

export default function Page() {
  const {
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
  } = useDashboardPage();

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => void loadData()}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => setShowModal(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {errorMessage ? (
            <Alert variant="danger" className="shadow-sm">
              {errorMessage}
            </Alert>
          ) : null}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FilesTable files={files} isLoading={isLoading} />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertsTable alerts={alerts} isLoading={isLoading} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <UploadFileModal
        show={showModal}
        isSubmitting={isSubmitting}
        title={title}
        onTitleChange={setTitle}
        onFileChange={setSelectedFile}
        onClose={() => setShowModal(false)}
        onSubmit={handleSubmit}
      />
    </Container>
  );
}
