import { configureStore } from "@reduxjs/toolkit";
import fileReducer from "./slices/fileSlice";

// reducer모음집.
export const store = configureStore({
  reducer: {
    files: fileReducer,
  },
});

// rootstate는 이제 저 reducer에 추가되는 상태관리값들의 타입들을 자동으로 추론해줘서 타입을 자동으로 업데이트해줌.
// 밑에 dispatch는 파일을 전달하는역할로 rootstate처럼 타입을 자동으로 업데이트해줌.
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
