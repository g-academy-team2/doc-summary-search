import FileUpload from "../components/upload/FileUpload";
import Sidebar from "../components/common/Sidebar";

function UploadPage() {
  return (
    <div className="upload-container m-5 flex divide-x">
      <Sidebar />
      <main className="upload-main w-8/10  border rounded-m p-10">
        <div className=" border border-dashed  rounded-4xl flex flex-col p-10 gap-4">
          <h1 className="text-center">아이콘 들어갈자리입니다.</h1>
          <FileUpload />
        </div>
      </main>
    </div>
  );
}

export default UploadPage;
