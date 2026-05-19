import { useState } from "react";
import { useFiles } from "../hooks/useFiles";
import Sidebar from "../components/common/Sidebar";
import SearchFileCard from "../components/search/SearchFileCard";

function SearchPage() {
  const [isOpen, setIsOpen] = useState(false);
  const { files, handleDelete } = useFiles();

  return (
    // pages/SearchPage.tsx
    <div className="Search-container flex m-5 divide-x min-h-screen">
      <Sidebar />

      <main className="Search-main w-8/10  border rounded-m  flex-1 flex flex-col p-4 pl-10 pb-6 ">
        {/* 상단 필터 버튼 영역 */}
        <div className="Search-containerflex gap-4 mb-4 ml-50">
          <div className="relative">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="Search-button relative cursor-pointer border rounded-4xl px-7 py-0.5 flex items-center w-28"
            >
              <span className="absolute left-1/2 -translate-x-1/2">필터</span>
              <span className={`ml-16 ${isOpen ? "rotate-180" : ""}`}>▼</span>
            </button>
            {isOpen && (
              <div
                className={`absolute top-8 left-0 border rounded-lg bg-white shadow-md z-10 w-28 overflow-hidden transition-all duration-100 ${isOpen ? "max-h-40 p-3" : "max-h-0"}`}
              >
                <ul className="space-y-1">
                  <li className="cursor-pointer hover:text-gray-400">IT</li>
                  <li className="cursor-pointer hover:text-gray-400">법률</li>
                  <li className="cursor-pointer hover:text-gray-400">법안</li>
                  <li className="cursor-pointer hover:text-gray-400">교육</li>
                  <li className="cursor-pointer hover:text-gray-400">기타</li>
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* 파일 카드 그리드 */}
        <div className="File-card grid grid-cols-3 gap-4 auto-cols-min">
          {files.map((file, index) => (
            <SearchFileCard
              key={index}
              file={file}
              onDelete={() => handleDelete(index)}
            />
          ))}
        </div>

        {/* 하단 검색 + 페이지네이션 */}
        <div className="Search-bar flex items-center justify-between mt-auto pt-4">
          <div className="border p-2 flex items-center px-2 py-2 ">
            <input
              name="text"
              type="text"
              placeholder="검색"
              className="outline-none flex-1"
            />
            <button className="Search-icon cursor-pointer text-gray-400">
              <span>아이콘</span>
            </button>
          </div>
          <div className="Page-container flex gap-2 text-4xl">
            <button>≪</button>
            <button>←</button>
            <button>1</button>
            <button>2</button>
            <button>3</button>
            <span>...</span>
            <button>→</button>
            <button>≫</button>
          </div>
        </div>
      </main>
    </div>
  );
}
export default SearchPage;
