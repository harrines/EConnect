import React, { useState, useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { FaClock, FaSignInAlt, FaSignOutAlt } from "react-icons/fa";
import { Baseaxios, LS  ,ipadr } from "../Utils/Resuse";

function Clockin() {
  const [Login, setLogin] = useState(false);

  const clockinapi = () => {
    const userId = LS.get("userid");
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    
    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: JSON.stringify({
        name: LS.get("name"),
        userid: userId
      }),
      redirect: "follow"
    };

    fetch(`${ipadr}/Clockin`, requestOptions)
      .then(response => response.json())
      .then(data => {
        if (data.message && data.message.includes("Clock-in successful")) {
          toast.success(data.message);
        } else {
          toast.info(data.message);
          setLogin(true);
        }
      })
      .catch(error => {
        toast.error("Clock-in failed. Please try again.");
        console.error(error);
      });
  };

  const clockoutapi = () => {
    const userId = LS.get("userid");
    
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    
    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: JSON.stringify({
        name: LS.get("name"),
        userid: userId
      }),
      redirect: "follow"
    };

    fetch(`${ipadr}/Clockout`, requestOptions)
      .then(response => response.json())
      .then(data => {
        if (data.message && data.message.includes("Clock-out successful")) {
          toast.success(data.message);
        } else {
          toast.success(data.message);
          setLogin(false);
        }
      })
      .catch(error => {
        toast.error("Clock-out failed. Please try again.");
        console.error(error);
      });
  };

  const previousDayClockoutApi = () => {
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    
    const requestOptions = {
      method: "POST",
      headers: myHeaders,np,
      body: JSON.stringify({
        name: LS.get("name"),
        userid: userid
      }),
      redirect: "follow"
    };

    fetch(`${ipadr}/PreviousDayClockout`, requestOptions)
      .catch(error => console.error(error));
  };

  // const autoClockoutApi = () => {
  //   const myHeaders = new Headers();
  //   myHeaders.append("Content-Type", "application/json");
    
  //   const requestOptions = {
  //     method: "POST",
  //     headers: myHeaders,
  //     body: JSON.stringify({
  //       name: "dhivya",
  //       userid: "6780c24108c4b3e2da6113ec"
  //     }),
  //     redirect: "follow"
  //   };

  //   fetch("http://127.0.0.1:8000/AutoClockout", requestOptions)
  //     .catch(error => console.error(error));
  // };

  // useEffect(() => {
  //   previousDayClockoutApi();
  //   autoClockoutApi();
    
  //   const interval = setInterval(() => {
  //     autoClockoutApi();
  //   }, 60000);

  //   return () => clearInterval(interval);
  // }, []);

  return (
    <div className="flex justify-center items-center pt-32">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-sm w-full border">
        <div className="flex flex-col items-center space-y-6">
          <div className="text-2xl font-bold text-blue-600 flex items-center space-x-2">
            <FaClock />
            <span>Productivity Dashboard</span>
          </div>
          <div className="flex justify-center space-x-4">
            <button
              className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-green-600 focus:ring-4 focus:ring-green-300"
              onClick={clockinapi}
            >
              <FaSignInAlt />
              <span>Clock In</span>
            </button>

            <button
              className="flex items-center space-x-2 px-6 py-3 bg-red-500 text-white text-lg font-semibold rounded-lg shadow-md hover:bg-red-600 focus:ring-4 focus:ring-red-300"
              onClick={clockoutapi}
            >
              <FaSignOutAlt />
              <span>Clock Out</span>
            </button>
          </div>
        </div>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={3000}
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

export default Clockin;