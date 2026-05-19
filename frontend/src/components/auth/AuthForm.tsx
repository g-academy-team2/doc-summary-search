import Input from "./AuthInput";

// type 설정은 일단 여기에 작성을 하나, 추후 types폴더를 생성해서 거기에 둘 생각입니다.
type Field = {
  name: string;
  type?: "text" | "password";
  placeholder: string;
  autoComplete?: string; // 브라우저 자동완성 호환용.
};

/**

filed는 { id: string, label: string, type: string }) 이런식의 필드의 타입을 정의한건데 일단 ㄱㄷ
valuese {email:email password: password} 2개의 값을 넣은 객체
errors => ex){ email: 에러메세지}
쉽게 설명하면 2개는 key값과 value값을 넣은 값이라고 미리 타입을 정의를 해준것입니다.
 */
type AuthFormProps = {
  title: string;
  fields: Field[];
  values: Record<string, string>;
  //   ?는 옵션처리하는것 에러가 들어갈수도있고 안들어갈수도있기때문.
  errors?: Record<string, string>;
  onChange: (name: string, value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
  success?: boolean;
  submitText: string;
  children?: React.ReactNode;
};

function AuthForm({
  title,
  fields,
  values,
  errors = {},
  onChange,
  onSubmit,
  loading,
  success,
  submitText,
  children,
}: AuthFormProps) {
  return (
    <main className="Auth-container min-h-screen flex items-center justify-center  px-4">
      <div className="w-full max-w-md">
        <div className="border border-[#2a2a35] rounded-2xl p-10">
          {/* HEADER */}
          <div className="Auth-header text-center mb-10">
            <div className="Auth-Logo text-4xl mb-4 ">로고나 아이콘자리</div>
            {/* 여기는 login , signup넣는 h2입니다. */}
            <h2 className="Auth-Title  text-3xl font-semibold">{title}</h2>
          </div>
          {/* 로그인이나 회원가입이 성공하면 success라고 유저에게 알려줍니다. */}
          {success ? (
            <div className="Auth-Sucess text-center text-white">Success</div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                onSubmit();
              }}
              className="Auth-Form space-y-6"
            >
              {fields.map((f) => (
                <Input
                  name={f.name}
                  key={f.name}
                  type={f.type}
                  value={values[f.name] || ""}
                  onChange={(v) => onChange(f.name, v)}
                  placeholder={f.placeholder}
                  error={errors?.[f.name]}
                  autoComplete={f.autoComplete}
                />
              ))}

              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 border rounded-md to-black font-semibold 
                ${loading ? "opacity-70" : "cursor-pointer"}
                `}
              >
                {loading ? "Loading..." : submitText}
              </button>
            </form>
          )}
          {children}
        </div>
      </div>
    </main>
  );
}

export default AuthForm;
