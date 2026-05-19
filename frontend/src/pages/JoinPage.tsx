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
        {
          name: "username",
          type: "text",
          placeholder: "Username",
          autoComplete: "username",
        },
        {
          name: "password",
          type: "password",
          placeholder: "Password",
          autoComplete: "new-password",
        },
        {
          name: "confirmPassword",
          type: "password",
          placeholder: "Confirm Password",
          autoComplete: "new-password",
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
