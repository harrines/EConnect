import React from "react";
import logo from "../assets/logo.png";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./login.css";
import { useNavigate } from "react-router-dom";
import { Authdata } from "../Utils/Authprovider";
import { Apisignin } from "../Api/Loginauth";
import { jwtDecode } from "jwt-decode";
import { LS } from "../Utils/Resuse";

export default function LoginPage() {
  const navigate = useNavigate();
  const { SetStatedata } = Authdata();

  const handleGoogleLogin = async (credentialResponse) => {
    try {
      let userDecode = jwtDecode(credentialResponse.credential);
      const res = await Apisignin({
        client_name: userDecode.name,
        email: userDecode.email,
      });
      const loggedIn = LS.get("isloggedin");
      const isAdmin  = LS.get("isadmin");
      if(loggedIn && isAdmin){
        navigate("admin/time", {
          state: { id: res.id, token: res.access_token },
        });
      }else if(loggedIn || isAdmin){
        navigate("User/Clockin_int", {
          state: { id: res.id, token: res.access_token },
        });
      } else{
        console.log("Invalid request")
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
        <div className="flex flex-col items-center justify-center p-8">
          <div className="text-center mb-6">
          <img src={logo} alt="Company Logo" className="h-32 mx-auto" />
            <h1 className="text-2xl font-bold text-gray-700 mt-4">
              Welcome to Econnect
            </h1>
          </div>
          <div className="w-full">
            <h2 className="text-xl font-semibold text-gray-600 mb-4 text-center">
              Sign in with Google
            </h2>
            <div className="flex justify-center">
              <GoogleOAuthProvider clientId="333036008565-7qkpcqr080na6l9fpcn492kc00ea2bv1.apps.googleusercontent.com">
                <GoogleLogin
                  onSuccess={handleGoogleLogin}
                  useOneTap
                />
              </GoogleOAuthProvider>
            </div>
          </div>
        </div>
      </div>

      <ToastContainer
        position="bottom-center"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}