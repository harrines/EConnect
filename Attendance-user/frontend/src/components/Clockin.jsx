import React, { useState, useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  FaClock,
  FaSignInAlt,
  FaSignOutAlt,
  FaSpinner,
  FaCheckCircle,
  FaTimesCircle,
} from "react-icons/fa";
import { LS, ipadr } from "../Utils/Resuse";

function Clockin() {
  const [Login, setLogin] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationAction, setConfirmationAction] = useState(null);
  const [lastAction, setLastAction] = useState(null);
  const [clockInTime, setClockInTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentStatus, setCurrentStatus] = useState("ready");

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    let interval;
    if (currentStatus === "clocked-in" && clockInTime) {
      interval = setInterval(() => {
        const now = new Date();
        setElapsedTime(Math.floor((now - clockInTime) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [currentStatus, clockInTime]);

  useEffect(() => {
    const savedStatus = localStorage.getItem("clockStatus");
    const savedClockInTime = localStorage.getItem("clockInTime");
    if (savedStatus) {
      setCurrentStatus(savedStatus);
      if (savedStatus === "clocked-in" && savedClockInTime) {
        setClockInTime(new Date(savedClockInTime));
        setLogin(true);
      }
    }
  }, []);

  const formatTime = (date) =>
    date.toLocaleTimeString("en-US", {
      hour12: true,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const formatElapsedTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const showConfirmationDialog = (action) => {
    setConfirmationAction(action);
    setShowConfirmation(true);
  };

  const hideConfirmationDialog = () => {
    setShowConfirmation(false);
    setConfirmationAction(null);
  };

  const executeAction = () => {
    if (confirmationAction === "clockin") clockinapi();
    else if (confirmationAction === "clockout") clockoutapi();
    hideConfirmationDialog();
  };

  const clockinapi = () => {
    const userId = LS.get("userid");
    setIsLoading(true);
    setLastAction("clock-in");

    fetch(`${ipadr}/Clockin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: LS.get("name"), userid: userId }),
    })
      .then((res) => res.json())
      .then((data) => {
        setIsLoading(false);
        if (data.message?.includes("Clock-in successful")) {
          const now = new Date();
          setClockInTime(now);
          setCurrentStatus("clocked-in");
          setLogin(true);
          localStorage.setItem("clockStatus", "clocked-in");
          localStorage.setItem("clockInTime", now.toISOString());
          toast.success(`✅ Clocked in at ${formatTime(now)}`);
        } else toast.info(data.message);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Clock-in failed. Try again.");
      });
  };

  const clockoutapi = () => {
    const userId = LS.get("userid");
    setIsLoading(true);
    setLastAction("clock-out");

    fetch(`${ipadr}/Clockout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: LS.get("name"), userid: userId }),
    })
      .then((res) => res.json())
      .then((data) => {
        setIsLoading(false);
        if (data.message?.includes("Clock-out successful")) {
          const now = new Date();
          setCurrentStatus("clocked-out");
          setLogin(false);
          setElapsedTime(0);
          localStorage.removeItem("clockStatus");
          localStorage.removeItem("clockInTime");
          toast.success(
            `👋 Clocked out at ${formatTime(
              now
            )}. Worked for ${formatElapsedTime(elapsedTime)}`
          );
        } else toast.info(data.message);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Clock-out failed. Try again.");
      });
  };

  return (
    <div className="relative min-h-[90vh] w-full flex flex-col items-center justify-center bg-gradient-to-br from-indigo-100 via-white to-cyan-100 p-6 overflow-hidden">
      {/* Animated gradient blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[300px] h-[300px] bg-purple-300 rounded-full blur-3xl opacity-40 animate-pulse"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[300px] h-[300px] bg-cyan-300 rounded-full blur-3xl opacity-40 animate-pulse"></div>

      {/* Real-time Clock Display */}
      <div className="text-2xl font-semibold text-gray-700 mb-6 tracking-wide drop-shadow-sm">
        🕒 {currentTime.toLocaleTimeString("en-US", { hour12: true })}
      </div>

      {/* Main Card */}
      <div className="backdrop-blur-xl bg-white/60 border border-gray-200 shadow-2xl rounded-3xl p-8 w-full max-w-2xl transition-all hover:shadow-[0_0_40px_rgba(0,0,0,0.1)]">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            E-Connect Productivity
          </h1>
          <p className="text-gray-500 text-sm">
            Manage your work hours seamlessly
          </p>
        </div>

        {/* Work Status */}
        <div className="flex flex-col items-center justify-center mb-10">
          {currentStatus === "clocked-in" ? (
            <div className="flex flex-col items-center">
              <FaCheckCircle className="text-green-500 text-5xl mb-3 drop-shadow-md" />
              <h2 className="text-2xl font-semibold text-green-600">
                You are Clocked In
              </h2>
              <p className="text-gray-500 mt-2">
                Started at {clockInTime && formatTime(clockInTime)}
              </p>
              <div className="text-4xl font-mono mt-3 text-green-700 tracking-wider">
                {formatElapsedTime(elapsedTime)}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <FaTimesCircle className="text-gray-400 text-5xl mb-3" />
              <h2 className="text-2xl font-semibold text-gray-600">
                You are not Clocked In
              </h2>
              <p className="text-gray-500 mt-2 text-sm">
                Click below to start your work session.
              </p>
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex justify-center gap-8">
          <button
            className={`flex items-center justify-center gap-3 px-8 py-4 rounded-full text-lg font-semibold transition-all duration-200 transform ${
              currentStatus === "clocked-in" || isLoading
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-green-500 text-white shadow-lg hover:scale-105 hover:bg-green-600"
            }`}
            onClick={() =>
              currentStatus !== "clocked-in" && !isLoading
                ? showConfirmationDialog("clockin")
                : null
            }
            disabled={currentStatus === "clocked-in" || isLoading}
          >
            {isLoading && lastAction === "clock-in" ? (
              <FaSpinner className="animate-spin" />
            ) : (
              <FaSignInAlt />
            )}
            {isLoading && lastAction === "clock-in"
              ? "Clocking In..."
              : "Clock In"}
          </button>

          <button
            className={`flex items-center justify-center gap-3 px-8 py-4 rounded-full text-lg font-semibold transition-all duration-200 transform ${
              currentStatus !== "clocked-in" || isLoading
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-red-500 text-white shadow-lg hover:scale-105 hover:bg-red-600"
            }`}
            onClick={() =>
              currentStatus === "clocked-in" && !isLoading
                ? showConfirmationDialog("clockout")
                : null
            }
            disabled={currentStatus !== "clocked-in" || isLoading}
          >
            {isLoading && lastAction === "clock-out" ? (
              <FaSpinner className="animate-spin" />
            ) : (
              <FaSignOutAlt />
            )}
            {isLoading && lastAction === "clock-out"
              ? "Clocking Out..."
              : "Clock Out"}
          </button>
        </div>

        {/* Footer Tip */}
        <p className="text-center text-gray-500 text-sm mt-8 border-t pt-4">
          {currentStatus === "clocked-in"
            ? "You're currently clocked in. Remember to clock out before leaving!"
            : "Click Clock In to begin tracking your productive time."}
        </p>
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 text-center w-[340px] animate-fadeIn">
            <div className="mb-4">
              {confirmationAction === "clockin" ? (
                <FaSignInAlt className="text-green-500 text-4xl mx-auto" />
              ) : (
                <FaSignOutAlt className="text-red-500 text-4xl mx-auto" />
              )}
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              {confirmationAction === "clockin"
                ? "Confirm Clock In"
                : "Confirm Clock Out"}
            </h3>
            <p className="text-gray-500 mb-6 text-sm">
              {confirmationAction === "clockin"
                ? "Start tracking your working hours now?"
                : "End your current work session?"}
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={hideConfirmationDialog}
                className="px-5 py-2 rounded-full bg-gray-200 text-gray-600 hover:bg-gray-300 font-medium transition"
              >
                Cancel
              </button>
              <button
                onClick={executeAction}
                className={`px-5 py-2 rounded-full text-white font-medium transition ${
                  confirmationAction === "clockin"
                    ? "bg-green-500 hover:bg-green-600"
                    : "bg-red-500 hover:bg-red-600"
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      <ToastContainer position="top-right" autoClose={4000} theme="colored" />
    </div>
  );
}

export default Clockin;
