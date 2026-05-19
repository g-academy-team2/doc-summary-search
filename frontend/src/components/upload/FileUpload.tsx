import { useDispatch, useSelector } from "react-redux";
import type { AppDispatch, RootState } from "../../store";
import { addFiles } from "../../store/slices/fileSlice";

// file upload
export default function FileUpload() {
  const dispatch = useDispatch<AppDispatch>();
  const files = useSelector((state: RootState) => state.files.files);

  // 임시 파일저장되는 로직
  const toFileItems = (files: File[]) =>
    files.map((file) => ({
      name: file.name,
      date: new Date()
        .toLocaleDateString("ko-KR")
        .replace(/\. /g, ".")
        .replace(".", ""),
      progress: 0,
      status: "uploading" as const,
    }));

  const handleFiles = (selectedFiles: File[]) => {
    dispatch(addFiles(toFileItems(selectedFiles)));
  };

  // 드래그 작동
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  // 드래그 파일놓음.
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    dispatch(addFiles(toFileItems(droppedFiles)));
    handleFiles(Array.from(e.dataTransfer.files));
  };

  // 실수로 파일올린경우 다른파일로 교체.
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    dispatch(addFiles(toFileItems(selectedFiles)));
    handleFiles(Array.from(e.target.files || []));
  };

  return (
    <div
      className="Fileupload-container flex flex-col items-center w-full"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <label className="Fileupload-label cursor-pointer">
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
        <p className="text-center text-gray-900/40">
          요약할 파일을 드래그&드랍
          <br />
          혹은 <span className="underline">직접 선택</span> 하세요
        </p>
      </label>
    </div>
  );
}
