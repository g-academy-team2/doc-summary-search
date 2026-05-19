import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";
import type { FileItem } from "../../types/file";

interface FileState {
  files: FileItem[];
}

const initialState: FileState = {
  files: [
    // 체크용 더미데이터
    { name: "파일명1.word", date: "2026.05.13" },
    { name: "파일명2.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
    { name: "파일명3.word", date: "2026.05.13" },
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
      state.files.push(...action.payload);
    },
    deleteFile: (state, action: PayloadAction<number>) => {
      state.files.splice(action.payload, 1);
    },
    clearFiles: (state) => {
      state.files = [];
    },
  },
});

export const { addFiles, deleteFile, clearFiles } = fileSlice.actions;
export default fileSlice.reducer;
