// type
interface FileUploadProps {
  files: File[];
  setFiles: React.Dispatch<React.SetStateAction<File[]>>;
}

// file upload
function FileUpload({ files, setFiles }: FileUploadProps) {
  // Drag event
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };
  //  Dragdrop event
  const handelDrop = (e: React.DragEvent) => {
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  };
  // file교체 하는경우
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  return (
    <div
      className="flex flex-col items-center w-full"
      onDragOver={handleDragOver}
      onDrop={handelDrop}
    >
      <label className="cursor-pointer">
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
        <p className="text-center  text-gray-900/40">
          요약할 파일을 드래그&드랍
          <br />
          혹은 <span className="underline">직접 선택</span> 하세요
        </p>
      </label>
    </div>
  );
}

export default FileUpload;
