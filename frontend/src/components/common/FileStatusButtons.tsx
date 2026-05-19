import type { FileItem } from "../../types/file";

interface FileStatusButtonsProps {
  file: FileItem;
  index: number;
  onSummarize: (index: number) => void;
  onDelete: (index: number) => void;
  size?: "sm" | "md";
}

export default function FileStatusButtons({
  file,
  index,
  onSummarize,
  onDelete,
  size = "md",
}: FileStatusButtonsProps) {
  const btnClass =
    size === "sm"
      ? "border px-1.5 py-0.5 rounded text-xs cursor-pointer hover:text-blue-500 transition-colors duration-200"
      : "border px-3 py-1 rounded cursor-pointer hover:text-blue-500 transition-colors duration-200";
  const spinClass = size === "sm" ? "w-3 h-3 border-2" : "w-5 h-5 border-4";
  const textClass = size === "sm" ? "text-xs" : "text-sm";
  const deleteClass = size === "sm" ? "text-sm" : "text-2xl";

  return (
    <div className="flex items-center gap-1">
      {file.status === "uploading" && (
        <div className="flex items-center gap-1">
          <span className={`text-gray-700 ${textClass}`}>업로드 중...</span>
          <div
            className={`${spinClass} border-gray-300 border-t-gray-600 rounded-full animate-spin`}
          />
        </div>
      )}

      {file.status === "idle" && (
        <button onClick={() => onSummarize(index)} className={btnClass}>
          요약하기
        </button>
      )}

      {file.status === "summarizing" && (
        <div className="flex items-center gap-1">
          <span className={`text-gray-500 ${textClass}`}>요약 중...</span>
          <div
            className={`${spinClass} border-gray-300 border-t-green-500 rounded-full animate-spin`}
          />
        </div>
      )}

      {file.status === "done" && (
        <div className="flex items-center gap-1">
          <button className={btnClass}>⬇️</button>
          <button className={`${btnClass}  `}>
            {size === "sm" ? "보기" : "요약보기"}
          </button>
        </div>
      )}

      <button
        onClick={() => onDelete(index)}
        className={`text-gray-500 hover:text-red-500 cursor-pointer ${deleteClass}`}
        disabled={file.status === "uploading" || file.status === "summarizing"}
      >
        ×
      </button>
    </div>
  );
}
