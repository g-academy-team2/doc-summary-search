import { useSelector } from "react-redux";
import { Link } from "react-router-dom";
import type { RootState } from "../../store";
import { useFiles } from "../../hooks/useFiles";
import FileStatusButtons from "./FileStatusButtons";

function Sidebar() {
  const files = useSelector((state: RootState) => state.files.files);
  const { handleDelete, handleSummarize } = useFiles();

  return (
    <aside className="Sidebar-container sticky top-0 w-2/10 border rounded-m flex flex-col justify-between h-screen ">
      <div>
        <h1 className="font-bold text-3xl">Logo</h1>
      </div>
      <div className="text-center overflow-y-auto">
        {files.length === 0 ? (
          <p>최근 업로드된 파일이 없습니다.</p>
        ) : (
          <ul>
            {files.map((file, index) => (
              <li
                key={index}
                className="border px-2 py-1 mb-1 rounded text-sm flex items-center justify-between"
              >
                <p>📄</p>
                <p className="truncate">{file.name}</p>
                <FileStatusButtons
                  file={file}
                  index={index}
                  onSummarize={handleSummarize}
                  onDelete={handleDelete}
                  size="sm"
                />
              </li>
            ))}
          </ul>
        )}
      </div>
      <ul className="Side-link-container pl-10 pb-5 space-y-1 text-2xl">
        <Link to="/search">
          <li className="hover:text-blue-500">검색</li>
        </Link>
        <Link to="/upload">
          <li className="hover:text-blue-500">파일 요약</li>
        </Link>
        <Link to="/login">
          <li className="hover:text-blue-500">로그아웃</li>
        </Link>
      </ul>
    </aside>
  );
}

export default Sidebar;
