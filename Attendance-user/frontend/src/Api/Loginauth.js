import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Baseaxios, LS } from '../Utils/Resuse';


export const Apisignup = async ({ email, password, name }) => {
  try {
    const response = await Baseaxios.post("/signup", {
      email,
      password,
      name,
    });

    const Comp = response.data;
    LS.save("userid", Comp.userid);
    LS.save("name", Comp.name);
    LS.save("email", Comp.email);
    LS.save("access_token", Comp.access_token);
    LS.save("id", Comp.id);
    LS.save("Auth", true);

    return Comp;
  } catch (err) {
    let msg = "Signup failed. Please try again.";
    if (err.response?.data?.detail) {
      msg = err.response.data.detail;
    }
    toast.error(msg);
    console.error("Signup API error:", err);
    return null;
  }
};

export const Apisignin = async ({ client_name, email }) => {
  try {
    const response = await Baseaxios.post("/Gsignin", {
      client_name,
      email,
    });

    const Comp = response.data;

    // Save everything to LS
    LS.save("name", Comp.name);
    LS.save("email", Comp.email);
    LS.save("userid", Comp.userid);
    LS.save("position", Comp.position);
    LS.save("department", Comp.department);
    LS.save("personal_email", Comp.personal_email);
    LS.save("date_of_joining", Comp.date_of_joining);
    LS.save("address", Comp.address);
    LS.save("education", Comp.education);
    LS.save("TL", Comp.TL);
    LS.save("phone", Comp.phone);
    LS.save("resume_link", Comp.resume_link);
    LS.save("skills", Comp.skills);
    LS.save("access_token", Comp.access_token);
    LS.save("id", Comp.id);
    LS.save("status", Comp.status);
    LS.save("Auth", true);
    LS.save("isadmin", Comp.isadmin);
    LS.save("isloggedin", Comp.isloggedin);

    toast.success("Login Successfully");
    return Comp;
  } catch (err) {
    let msg = "Signin failed. Please try again.";
    if (err.response?.data?.detail) {
      msg = err.response.data.detail;
    }
    toast.error(msg);
    console.error("Signin API error:", err);
    return null;
  }
};
