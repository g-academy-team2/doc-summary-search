export interface FileItem {
  name: string;
  date: string;
  progress?: number; // 0~100
  extension: "pdf" | "pptx" | "docx" | "hwp";
  status: "uploading" | "summarizing" | "done" | "failed";
}
