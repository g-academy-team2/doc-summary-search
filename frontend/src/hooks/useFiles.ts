import { useDispatch, useSelector } from "react-redux";
import type { RootState, AppDispatch } from "../store";
import {
  deleteFile,
  updateProgress,
  updateStatus,
} from "../store/slices/fileSlice";

// file 삭제로직 겹쳐서 생성.
export function useFiles() {
  const dispatch = useDispatch<AppDispatch>();
  const files = useSelector((state: RootState) => state.files.files);

  const handleDelete = (index: number) => {
    dispatch(deleteFile(index));
  };

  const handleSummarize = (index: number) => {
    dispatch(updateStatus({ index, status: "summarizing" }));

    // 백엔드 연결 전 가짜 progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      dispatch(updateProgress({ index, progress }));
      if (progress >= 100) {
        dispatch(updateStatus({ index, status: "done" }));
        clearInterval(interval);
      }
    }, 200);
  };

  return { files, handleDelete, handleSummarize };
}
