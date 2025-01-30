import { comma } from "postcss/lib/list";
import { Baseaxios, LS } from "../Utils/Resuse";
import { toast } from "react-hot-toast";
export const Apisignup = async ({ email, password, name }) => {
  const response = await Baseaxios.post("/signup", {
    email: email,
    password: password,
    name: name,
  }).catch((err) => {
    const a = err.response.data.detail;
    toast.error(a);
    throw new Error(a);
  });

  const Comp = response.data;
  LS.save("userid", Comp.id);
  LS.save("name", Comp.name);
  LS.save("access_token", Comp.access_token);
  LS.save("Auth", true);
  LS.save("isManager",)

  return Comp;
};

export const Apisignin = async ({ client_name, email }) => {
  const response = await Baseaxios.post("/Gsignin", {
    client_name: client_name,
    email: email,
  }).catch((err) => {
    const a = err.response.data.detail;
    toast.error(a);
    throw new Error(a);
  });
  const Comp = response.data;
  LS.save("name", Comp.name);
  LS.save("userid", Comp.id);
  LS.save("position",Comp.position);
  LS.save("department",Comp.department)
  LS.save("access_token", Comp.access_token);
  LS.save("Auth", true);
  LS.save("isadmin", Comp.isadmin);
  LS.save("isloggedin", Comp.isloggedin);
  // LS.save("isManager",Comp.is)
  toast.success("Login Successfully");
  return Comp;
};


