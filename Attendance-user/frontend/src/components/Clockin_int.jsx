import React, { useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { FaPlay, FaStop } from "react-icons/fa";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Baseaxios, LS } from "../Utils/Resuse";

function Clockin_int() {
  const navigate = useNavigate();
  const [isClockedIn, setIsClockedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [actionType, setActionType] = useState(null);
  const [showBackButton, setShowBackButton] = useState(false);

  const showConfirmation = (type) => {
    setActionType(type);
    setShowConfirm(true);
  };

  const hideConfirmation = () => {
    setShowConfirm(false);
    setActionType(null);
  };

  const executeAction = () => {
    if (actionType === "clockin") {
      handleClockIn();
    } else if (actionType === "clockout") {
      handleClockOut();
    }
    hideConfirmation();
  };

  const handleClockIn = () => {
    const userid = LS.get("userid");
    const userName = LS.get("name");
    setIsLoading(true);
    const time = new Date().toLocaleTimeString();

    Baseaxios.post("/Clockin", { userid, name: userName, time })
      .then(() => {
        setIsLoading(false);
        setIsClockedIn(true);
        toast.success(`✅ Clocked in successfully at ${time}`);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Failed to clock in. Please try again.");
      });
  };

  const handleClockOut = () => {
    const userid = LS.get("userid");
    const userName = LS.get("name");
    setIsLoading(true);
    const time = new Date().toLocaleTimeString();

    Baseaxios.post("/Clockout", { userid, name: userName, time })
      .then(() => {
        setIsLoading(false);
        setIsClockedIn(false);
        toast.success(`✅ Clocked out successfully at ${time}`);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Failed to clock out. Please try again.");
      });
  };

  return (
    <div className="min-h-[90vh] w-full p-8 bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-sm flex flex-col items-center justify-center relative transition-all duration-300">
      {/* Confirmation Popup */}
      {showConfirm && (
        <div className="absolute inset-0 bg-white/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-200 text-center w-80">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              {actionType === "clockin" ? "Confirm Clock In" : "Confirm Clock Out"}
            </h3>
            <p className="text-gray-500 mb-5">
              {actionType === "clockin"
                ? "Do you want to start your work day now?"
                : "Do you want to end your work session now?"}
            </p>
            <div className="flex gap-3">
              <button
                onClick={hideConfirmation}
                className="flex-1 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100 transition"
              >
                Cancel
              </button>
              <button
                onClick={executeAction}
                className={`flex-1 py-2 rounded-lg text-white transition ${
                  actionType === "clockin"
                    ? "bg-emerald-500 hover:bg-emerald-600"
                    : "bg-rose-500 hover:bg-rose-600"
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="w-full flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
        <h1 className="text-3xl font-semibold text-gray-800">
          Welcome, <span className="text-blue-600">{LS.get("name")}</span> 👋
        </h1>

        {!showBackButton ? (
          <Link
            to={"Clockdashboard"}
            onClick={() => setShowBackButton(true)}
            className="px-5 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            View Details
          </Link>
        ) : (
          <button
            onClick={() => {
              setShowBackButton(false);
              navigate("/User/Clockin_int");
            }}
            className="px-5 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
          >
            Go Back
          </button>
        )}
      </div>

      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-md w-full max-w-lg p-10 flex flex-col items-center border border-gray-100 transition">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            {isClockedIn ? "You're Clocked In" : "Ready to Start Work?"}
          </h2>
          <p className="text-gray-500">
            {isClockedIn
              ? "Click below when you're done for the day."
              : "Click below to start your work session."}
          </p>
        </div>

        <div className="flex gap-4">
          {!isClockedIn ? (
            <button
              onClick={() => showConfirmation("clockin")}
              disabled={isLoading}
              className="flex items-center gap-2 px-6 py-3 bg-emerald-500 text-white rounded-xl shadow hover:bg-emerald-600 disabled:opacity-50 transition"
            >
              <FaPlay /> Clock In
            </button>
          ) : (
            <button
              onClick={() => showConfirmation("clockout")}
              disabled={isLoading}
              className="flex items-center gap-2 px-6 py-3 bg-rose-500 text-white rounded-xl shadow hover:bg-rose-600 disabled:opacity-50 transition"
            >
              <FaStop /> Clock Out
            </button>
          )}
        </div>
      </div>

      <Outlet />
      <ToastContainer position="top-right" autoClose={4000} />
    </div>
  );
}

export default Clockin_int;
