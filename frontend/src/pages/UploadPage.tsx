import { useFiles } from "../hooks/useFiles";
import FileUpload from "../components/upload/FileUpload";
import Sidebar from "../components/common/Sidebar";
import FileStatusButtons from "../components/common/FileStatusButtons";

function UploadPage() {
  const { files, handleDelete, handleSummarize } = useFiles();

  return (
    <div className="upload-container m-5 flex divide-x">
      <Sidebar />

      <main className="upload-main w-8/10 border rounded-m p-10">
        {/* 업로드 영역 */}
        <div className="border border-dashed rounded-4xl flex flex-col p-10 gap-4">
          <h1 className="text-center">아이콘 들어갈자리입니다.</h1>
          <FileUpload />
        </div>

        {/* 파일 리스트 */}
        <ul className="mt-5">
          {files.map((file, index) => (
            <li
              key={index}
              className="border px-4 py-3 flex items-center justify-between mb-2 rounded"
            >
              {/* 왼쪽 */}
              <div className="flex items-center gap-2 min-w-40">
                <p>📄</p>
                <p className="font-medium max-w-110 truncate">{file.name}</p>
              </div>

              {/* 가운데 상태 */}
              <div className="flex-1 mx-4">
                {/* 요약 중 */}
                {file.status === "summarizing" && (
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-gray-300 border-t-green-500 rounded-full animate-spin" />
                      <span className="text-sm text-gray-500">요약 중...</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-300 ${
                          (file.progress ?? 0) >= 50
                            ? "bg-green-500"
                            : "bg-blue-400"
                        }`}
                        style={{ width: `${file.progress ?? 0}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* 오른쪽 버튼 */}
              <div className="flex items-center gap-2">
                {/* 업로드 중 */}
                {file.status === "uploading" && (
                  <div className="flex items-center gap-2">
                    <span className="text-gray-700 font-medium">
                      업로드 중...
                    </span>
                    <div className="w-5 h-5 border-4 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                  </div>
                )}

                {/* idle → 요약하기 */}
                {file.status === "idle" && (
                  <button
                    onClick={() => handleSummarize(index)}
                    className="border px-3 py-1 rounded hover:bg-gray-100 cursor-pointer"
                  >
                    요약하기
                  </button>
                )}

                {/* done → 다운로드 + 요약보기 */}
                {file.status === "done" && (
                  <>
                    <button className="border px-3 py-1 rounded hover:bg-gray-100 cursor-pointer">
                      ⬇️ 다운로드
                    </button>
                    <button
                      onClick={() => console.log("요약보기", file)}
                      className="px-3 py-1 rounded bg-green-500 text-white cursor-pointer"
                    >
                      요약보기
                    </button>
                  </>
                )}

                {/* 삭제 */}
                <button
                  onClick={() => handleDelete(index)}
                  className="cursor-pointer text-2xl text-gray-500 hover:text-red-500"
                  disabled={
                    file.status === "uploading" || file.status === "summarizing"
                  }
                >
                  ×
                </button>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

export default UploadPage;
