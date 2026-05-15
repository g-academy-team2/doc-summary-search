import { useState } from "react";
import { Link } from "react-router-dom";
import AuthForm from "../components/auth/AuthForm";

// 로그인페이지
function LoginPage() {
  const [values, setValues] = useState({
    email: "",
    password: "",
  });
  return (
    <>
      <AuthForm
        title="Log In"
        fields={[
          { name: "email", type: "email", placeholder: "Email" },
          { name: "password", type: "password", placeholder: "Password" },
        ]}
        values={values}
        onChange={(name, value) => {
          setValues((prev) => ({ ...prev, [name]: value }));
        }}
        onSubmit={() => console.log("login", values)}
        submitText="Log In"
      >
        <div className="text-center mt-4 text-blue-400">
          <Link to="/join">회원가입</Link>
        </div>
      </AuthForm>
    </>
  );
}

export default LoginPage;
