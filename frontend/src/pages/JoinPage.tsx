import { useState } from "react";
import AuthForm from "../components/auth/AuthForm";
function JoinPage() {
  const [values, setValues] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  return (
    <AuthForm
      title="Create Account"
      fields={[
        { name: "email", type: "email", placeholder: "Email" },
        { name: "password", type: "password", placeholder: "Password" },
        {
          name: "confirmPassword",
          type: "password",
          placeholder: "Confirm Password",
        },
      ]}
      values={values}
      onChange={(name, value) => {
        setValues((prev) => ({ ...prev, [name]: value }));
      }}
      onSubmit={() => console.log("join", values)}
      submitText="Join"
    />
  );
}

export default JoinPage;
