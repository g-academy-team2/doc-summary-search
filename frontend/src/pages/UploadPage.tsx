import { useState } from "react";
import FileUpload from "../components/upload/FileUpload";
function UploadPage() {
  // file 상태관리
  const [files, setFiles] = useState<File[]>([]);

  return (
    <div className="m-5 flex divide-x">
      <aside className="w-3/10 border rounded-m flex flex-col justify-between h-[calc(100vh-40px)]">
        <div>
          <h1 className="font-bold text-3xl">Logo</h1>
        </div>
        <div className="text-center">
          {files.length === 0 ? (
            <p>최근 업로드된 파일이 없습니다.</p>
          ) : (
            <ul>
              {files.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          )}
        </div>
        <ul className="pl-10 pb-5 space-y-1  text-2xl">
          <li>검색</li>
          <li>파일 요약</li>
          <li>로그아웃</li>
        </ul>
      </aside>
      <main className="w-7/10  border rounded-m p-10">
        <div className=" border border-dashed  rounded-4xl flex flex-col p-10 gap-4">
          <h1 className="text-center">아이콘 들어갈자리입니다.</h1>
          <FileUpload files={files} setFiles={setFiles} />
        </div>
      </main>
    </div>
  );
}

export default UploadPage;
