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

  // Time updater
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Track elapsed work time
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

  // Load saved state
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

  // Confirm dialog handlers
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
        toast.error("❌ Clock-in failed. Check your connection.");
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
    <div className="w-full min-h-[90vh] bg-gradient-to-br from-blue-50 to-gray-100 flex items-center justify-center p-6">
      {/* Confirmation Dialog */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-2xl w-80 text-center">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">
              {confirmationAction === "clockin"
                ? "Confirm Clock In"
                : "Confirm Clock Out"}
            </h3>
            <p className="text-gray-500 mb-6">
              {confirmationAction === "clockin"
                ? "Start your work session now?"
                : "End your work session now?"}
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={hideConfirmationDialog}
                className="px-4 py-2 rounded-md bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium transition-all"
              >
                Cancel
              </button>
              <button
                onClick={executeAction}
                className={`px-4 py-2 rounded-md text-white font-medium transition-all ${
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

      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl p-8 border border-gray-200">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center text-blue-600 text-3xl font-bold mb-2">
            <FaClock className="mr-2" /> Productivity Dashboard
          </div>
          <p className="text-gray-500 text-sm">
            Manage your work hours efficiently
          </p>
        </div>

        {/* Status Section */}
        <div className="bg-gradient-to-r from-blue-50 to-gray-50 rounded-xl p-6 border border-gray-200 mb-8 text-center">
          <div className="text-lg font-semibold text-gray-700 mb-2">
            Current Status
          </div>
          <div className="flex justify-center items-center gap-2 mb-4">
            {currentStatus === "clocked-in" ? (
              <>
                <FaCheckCircle className="text-green-500 text-2xl" />
                <span className="text-green-600 font-semibold text-lg">
                  Clocked In
                </span>
              </>
            ) : (
              <>
                <FaTimesCircle className="text-gray-400 text-2xl" />
                <span className="text-gray-500 font-semibold text-lg">
                  Not Clocked In
                </span>
              </>
            )}
          </div>

          <div className="bg-white border rounded-xl py-4 px-6 inline-block shadow-sm">
            {currentStatus === "clocked-in" ? (
              <>
                <div className="text-gray-600 text-sm mb-1">Work Duration</div>
                <div className="text-3xl font-mono font-bold text-green-600 mb-1">
                  {formatElapsedTime(elapsedTime)}
                </div>
                <div className="text-xs text-gray-500">
                  Started at {clockInTime && formatTime(clockInTime)}
                </div>
              </>
            ) : (
              <div className="text-gray-400 text-sm">
                Clock in to start tracking your time.
              </div>
            )}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex justify-center gap-6">
          <button
            className={`flex items-center justify-center gap-3 px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-200 shadow-md ${
              currentStatus === "clocked-in" || isLoading
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-green-500 hover:bg-green-600 text-white hover:shadow-lg"
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
            className={`flex items-center justify-center gap-3 px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-200 shadow-md ${
              currentStatus !== "clocked-in" || isLoading
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-red-500 hover:bg-red-600 text-white hover:shadow-lg"
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

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm mt-6 border-t pt-4">
          {currentStatus === "clocked-in"
            ? "You're clocked in. Clock out when you're done working."
            : "Click 'Clock In' to start your work session."}
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={4000} theme="colored" />
    </div>
  );
}

export default Clockin;
