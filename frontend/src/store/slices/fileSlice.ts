import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { FileItem } from "../../types/file";

// 파일 전역상태관리
interface FileState {
  files: FileItem[];
}

const initialState: FileState = {
  files: [
    {
      name: "테스트1.pdf",
      date: "2026.05.19",
      progress: 0,
      status: "uploading",
    },
    {
      name: "테스트2.docx",
      date: "2026.05.19",
      progress: 40,
      status: "summarizing",
    },
    {
      name: "테스트3.pdf",
      date: "2026.05.19",
      progress: 0,
      status: "idle",
    },
    {
      name: "테스트4.jpg",
      date: "2026.05.19",
      progress: 100,
      status: "done",
    },
  ],
};

/* 
파일생성, 파일삭제, 파일리스트 비우기 => 로그아웃시 사용자가 바뀌니 비워줌.
사용자가 로그인하면 그때 유저의 파일을 담아줌.
*/
const fileSlice = createSlice({
  name: "files",
  initialState,
  reducers: {
    addFiles: (state, action: PayloadAction<FileItem[]>) => {
      const newFiles = action.payload.filter(
        (newFile) =>
          !state.files.some((existing) => existing.name === newFile.name),
      );
      state.files.push(...newFiles.map((file) => ({ ...file, progress: 0 })));
    },
    updateProgress: (
      state,
      action: PayloadAction<{ index: number; progress: number }>,
    ) => {
      state.files[action.payload.index].progress = action.payload.progress;
    },
    updateStatus: (
      state,
      action: PayloadAction<{ index: number; status: FileItem["status"] }>,
    ) => {
      state.files[action.payload.index].status = action.payload.status;
    },
    deleteFile: (state, action: PayloadAction<number>) => {
      state.files.splice(action.payload, 1);
    },
    clearFiles: (state) => {
      state.files = [];
    },
  },
});

export const {
  addFiles,
  updateProgress,
  deleteFile,
  clearFiles,
  updateStatus,
} = fileSlice.actions;
export default fileSlice.reducer;
