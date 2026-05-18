// 타입을 다른모듈에서 가져오는경우 import type규칙이 존재합니다.
import type { FileItem } from "../../types/file";

interface SearchFileCardProps {
  file: FileItem;
  onDelete: () => void;
}

export default function SearchFileCard({
  file,
  onDelete,
}: SearchFileCardProps) {
  return (
    <div className="File-card-container relative border p-3 flex items-center justify-between">
      {/* 우상단 X 버튼 File-card-esc */}
      <button
        onClick={onDelete}
        className="absolute -top-1 right-2 text-2xl cursor-pointer mr-1"
      >
        ×
      </button>

      {/* 왼쪽 아이콘 + 파일정보 */}
      <div className="File-card-icon flex items-center gap-2">
        <span className="text-2xl">📄</span>
        <div className="File-card-detail">
          <p className="font-medium">{file.name}</p>
          <p className="text-sm text-gray-400">요약일:{file.date}</p>
        </div>
      </div>

      {/* 오른쪽 다운로드 + 요약버튼 */}
      <div className="File-card-download-container flex items-center gap-2 ">
        <button className="cursor-pointer text-2xl">⬇️</button>
        <button className="border px-1 py-1 cursor-pointer text-sm">
          요약보기
        </button>
      </div>
    </div>
  );
}
