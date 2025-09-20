import Headlogo from "../assets/rbg2.png";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { FiLogOut, FiUser } from "react-icons/fi";
import { LS } from "../Utils/Resuse";

// Modal component
const Modal = ({ show, onClose, onConfirm, message }) => {
  if (!show) return null;

  return (
    <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50 z-50 ">
      <div className="bg-blue-100 p-4 rounded-lg">
        <p className="mb-3 text-black font-poppins">{message}</p>
        <hr className="border-gray-400" />
        <div className="flex flex-row">
          <button
            className="bg-red-400 hover:bg-red-500 text-white w-1/2 px-4 py-2 mt-4 rounded mr-2 font-poppins"
            onClick={onConfirm}
          >
            Yes
          </button>
          <button
            className="bg-gray-300 hover:bg-gray-400 text-black w-1/2 px-4 py-2 mt-4 rounded font-poppins"
            onClick={onClose}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

const Sidebar = ({ userPicture, userName, isLoggedIn, onLogout }) => {
  const navigate = useNavigate(); // Declare navigate only once
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const handleLogoutConfirm = () => {
    toast.success("Successfully logged out!", {
      position: "top-right",
      autoClose: 1000,
      onClose: () => {
        navigate("/"); // Redirect after logout
        setShowLogoutModal(false);
        onLogout();
      },
    });
  };

  const handleLogoutCancel = () => {
    setShowLogoutModal(false);
  };

  const handleClick = () => {
    navigate("/User/profile");
  };
  const loggedIn = LS.get("isloggedin");
  const isAdmin = LS.get("isadmin");
  const isManager=LS.get("position");
  const isDepart=LS.get("department");

  const userid=LS.get('id');

  return (
    <div className="flex flex-col min-h-screen w-64 bg-blue-600 text-white shadow-lg border-r">
      {/* Logo Section */}
      <div className="p-4 border-b-2 border-white border-purple-900 flex items-center justify-center">
        <img src={Headlogo} alt="Logo" className="h-16" />
      </div>

      {/* Links Section */}
      <div className="flex flex-col mt-6">
        {loggedIn && isAdmin ? (
          <>
            <Link to="time" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <circle cx="12" cy="12" r="10" strokeWidth="2" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6l3 3" />
                </svg>
                <span className="font-medium">Time Management</span>
              </div>
            </Link>

            <Link to="leave" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
                  />
                </svg>
                <span className="font-medium">Leave Management</span>
              </div>
            </Link>

            <Link to="employee" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="2" />
                  <circle cx="16" cy="8" r="3" stroke="currentColor" strokeWidth="2" />
                  <circle cx="12" cy="16" r="3" stroke="currentColor" strokeWidth="2" />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18a6 6 0 016-6h4a6 6 0 016 6"
                  />
                </svg>
                <span className="font-medium">Employee List</span>
              </div>
            </Link>

            <Link to="newUser" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 4a4 4 0 110 8 4 4 0 010-8zM6 20v-1a6 6 0 0112 0v1M16 11h6m-3-3v6"
                  />
                </svg>
                <span className="font-medium">Add Employee</span>
              </div>
            </Link>
          </>
        ) : loggedIn && !isAdmin && (
          <>
            <Link to="Clockin_int" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <circle cx="12" cy="12" r="10" strokeWidth="2" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6l3 3" />
                </svg>
                <span className="font-medium">Time Management</span>
              </div>
            </Link>

            <Link to="Leave" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
                  />
                </svg>
                <span className="font-medium">Leave Management</span>
              </div>
            </Link>

           {isDepart !== "HR" && (
            <Link to="todo" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 3h12M6 7h12M6 11h12M6 15h12M6 19h12" />
                </svg>
                <span className="font-medium">Task List</span>
              </div>
            </Link>
           )}

            {/* <Link to={`${userid}`} className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 3h12M6 7h12M6 11h12M6 15h12M6 19h12" />
                </svg>
                <span className="font-medium">Task Assign</span>
              </div>
            </Link> */}
          </>
        )
        }
        
        {
          loggedIn && isManager=="Manager" ?(
          <>

             {/* 🔹 New Manager–Employee connection tab */}
      <Link to="manager-employee" className="sidebar-item">
        <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
               stroke="currentColor" className="w-6 h-6 mr-3 text-white">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                  d="M6 3h12M6 7h12M6 11h12M6 15h12M6 19h12"/>
          </svg>
          <span className="font-medium">Employee Task Progress</span>
        </div>
      </Link>


            <Link to="LeaveManage" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
                  />
                </svg>
                <span className="font-medium">Employee Leave Management</span>
              </div>
            </Link>

           
          </>
          ): loggedIn && isDepart=="HR" && (
           <>
             {/* 🔹 New HR–Manager connection tab */}
      <Link to="hr-manager" className="sidebar-item">
        <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
               stroke="currentColor" className="w-6 h-6 mr-3 text-white">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                  d="M6 3h12M6 7h12M6 11h12M6 15h12M6 19h12"/>
          </svg>
          <span className="font-medium">Manager Task Progress</span>
        </div>
      </Link>
           <Link to="LeaveManage" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
                  />
                </svg>
                <span className="font-medium">Employee Leave Management</span>
              </div>
            </Link>
            <Link to="newUser" className="sidebar-item">
              <div className="flex items-center p-4 hover:bg-blue-700 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6 mr-3 text-white"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 4a4 4 0 110 8 4 4 0 010-8zM6 20v-1a6 6 0 0112 0v1M16 11h6m-3-3v6"
                  />
                </svg>
                <span className="font-medium">Add Employee</span>
              </div>
            </Link>
           </>
          )
        }
      </div>

      {/* Footer Section */}
      <div className="mt-auto border-t-2 border-white border-purple-900 p-4 flex justify-around">
        <FiLogOut
          size={24}
          className="cursor-pointer hover:text-red-500"
          onClick={() => setShowLogoutModal(true)}
        />
        <FiUser
          size={24}
          className="cursor-pointer "
          onClick={() => {
            if (loggedIn && !isAdmin) {
              navigate("/User/profile");
            } else if (loggedIn && isAdmin) {
              navigate("/admin/profile");
            }
          }}

        />
      </div>

      {/* Logout Modal */}
      <Modal
        show={showLogoutModal}
        onClose={handleLogoutCancel}
        onConfirm={handleLogoutConfirm}
        message="Are you sure you want to logout?"
      />

      <ToastContainer position="top-right" autoClose={1000} hideProgressBar theme="light" />
    </div>
  );
};

export default Sidebar;