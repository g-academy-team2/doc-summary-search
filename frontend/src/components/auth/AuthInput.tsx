import { useState } from "react";
// input 타입 정의 이게 타입에 text냐 email이냐 password따라 갈림.
// type 설정은 일단 여기에 작성을 하나, 추후 types폴더를 생성해서 거기에 둘 생각입니다.
type InputProps = {
  type?: "text" | "email" | "password";
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  error?: string;
};

// 일단 기본적으로 text타입으로 정의를 함.
export default function Input({
  type = "text",
  value,
  onChange,
  placeholder,
  error,
}: InputProps) {
  const isPassword = type === "password";
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      {/* input의 타입이 password일경우 password를 확인하는 checkpassword input을 추가함. */}
      <input
        type={isPassword ? (show ? "text" : "password") : type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full bg-[#1a1a25] border border-[#2a2a35] rounded-md px-4 py-4 text-white 
        ${isPassword ? "pr-12" : ""}`}
      />
      {/* 비밀번호 가리기 보이기 기능 */}
      {isPassword && (
        <button
          type="button"
          onClick={() => setShow(!show)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
        >
          button
        </button>
      )}
      {error && <p className="text-pink-500 text-xs mt-1">{error}</p>}
    </div>
  );
}
