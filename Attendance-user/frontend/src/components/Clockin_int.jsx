import React, { useState, useEffect } from "react";
import { useLocation, Link, Outlet, useNavigate } from "react-router-dom";
import { FaPlay, FaStop, FaCheckCircle } from "react-icons/fa";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Baseaxios, LS } from "../Utils/Resuse";

function Clockin_int() {
  const location = useLocation();
  const navigate = useNavigate();

  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [Login, Setlogin] = useState(false);
  const [showBackButton, setShowBackButton] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationAction, setConfirmationAction] = useState(null);

  useEffect(() => {
    const storedStartTime = parseInt(localStorage.getItem("startTime"));
    const storedElapsedTime = parseInt(localStorage.getItem("elapsedTime"));
    const storedIsRunning = localStorage.getItem("isRunning") === "true";
    const storedLogin = localStorage.getItem("Login") === "true";

    if (!isNaN(storedStartTime)) setStartTime(storedStartTime);
    if (!isNaN(storedElapsedTime)) setElapsedTime(storedElapsedTime);
    setIsRunning(storedIsRunning);
    Setlogin(storedLogin);
  }, []);

  useEffect(() => {
    localStorage.setItem("startTime", startTime);
    localStorage.setItem("elapsedTime", elapsedTime);
    localStorage.setItem("isRunning", isRunning);
    localStorage.setItem("Login", Login);
  }, [startTime, elapsedTime, isRunning, Login]);

  useEffect(() => {
    let timer;
    if (isRunning) {
      timer = setInterval(() => {
        setElapsedTime(Date.now() - startTime);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isRunning, startTime]);

  const toggleTimer = () => {
    Setlogin(true);
    if (isRunning) {
      setIsRunning(false);
    } else {
      setStartTime(Date.now() - elapsedTime);
      setIsRunning(true);
    }
  };

  const formatTime = (date) =>
    date.toLocaleTimeString("en-US", {
      hour12: true,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

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

  const resetTimer = () => {
    Setlogin(false);
    setIsRunning(false);
    setElapsedTime(0);
    setStartTime(null);
  };

  const clockinapi = () => {
    const userid = LS.get("userid");
    const userName = LS.get("name");
    setIsLoading(true);
    const currentDate = new Date();
    const time = currentDate.toLocaleTimeString();

    Baseaxios.post("/Clockin", { userid, name: userName, time })
      .then(() => {
        setIsLoading(false);
        toggleTimer();
        toast.success(`✅ Clocked in at ${formatTime(currentDate)}!`);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Failed to clock in. Try again.");
      });
  };

  const clockoutapi = () => {
    const userid = LS.get("userid");
    const userName = LS.get("name");
    setIsLoading(true);
    const currentDate = new Date();
    const time = currentDate.toLocaleTimeString();

    Baseaxios.post("/Clockout", { userid, name: userName, time })
      .then(() => {
        setIsLoading(false);
        const workDuration = formatElapsedTime(elapsedTime);
        resetTimer();
        toast.success(`✅ Clocked out! Total: ${workDuration}`);
      })
      .catch(() => {
        setIsLoading(false);
        toast.error("❌ Failed to clock out. Try again.");
      });
  };

  const formatElapsedTime = (time) => {
    const seconds = Math.floor((time / 1000) % 60);
    const minutes = Math.floor((time / (1000 * 60)) % 60);
    const hours = Math.floor(time / (1000 * 60 * 60));
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  return (
    <div className="p-10 bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-md min-h-[90vh] w-full transition-all">
      {/* Confirmation Dialog */}
      {showConfirmation && (
        <div className="absolute inset-0 flex items-center justify-center backdrop-blur-sm bg-white/60 z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-80 border border-gray-200 text-center">
            <h3 className="text-xl font-semibold mb-2 text-gray-700">
              {confirmationAction === "clockin"
                ? "Confirm Clock In"
                : "Confirm Clock Out"}
            </h3>
            <p className="text-gray-500 mb-4">
              {confirmationAction === "clockin"
                ? "Start your work timer now?"
                : "End your work session now?"}
            </p>
            <div className="flex gap-3">
              <button
                onClick={hideConfirmationDialog}
                className="flex-1 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100 transition"
              >
                Cancel
              </button>
              <button
                onClick={executeAction}
                className={`flex-1 py-2 rounded-lg text-white transition ${
                  confirmationAction === "clockin"
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

      <div className="flex justify-between items-center border-b pb-4 mb-6">
        <h1 className="text-3xl font-semibold text-gray-800">
          Welcome, <span className="text-blue-600">{LS.get("name")}</span> 👋
        </h1>

        {!showBackButton ? (
          <Link
            to={"Clockdashboard"}
            onClick={() => setShowBackButton(true)}
            className="px-5 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition"
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

      {/* Clock Info */}
      <div className="text-center py-10">
        <div className="text-6xl font-mono text-gray-800 mb-6">
          {formatElapsedTime(elapsedTime)}
        </div>

        <div className="flex justify-center gap-4">
          <button
            onClick={() => showConfirmationDialog("clockin")}
            disabled={isRunning || isLoading}
            className="flex items-center gap-2 px-5 py-3 bg-emerald-500 text-white rounded-lg shadow hover:bg-emerald-600 disabled:opacity-50 transition"
          >
            <FaPlay /> Clock In
          </button>

          <button
            onClick={() => showConfirmationDialog("clockout")}
            disabled={!isRunning || isLoading}
            className="flex items-center gap-2 px-5 py-3 bg-rose-500 text-white rounded-lg shadow hover:bg-rose-600 disabled:opacity-50 transition"
          >
            <FaStop /> Clock Out
          </button>
        </div>
      </div>

      <Outlet />

      <ToastContainer position="top-right" autoClose={4000} />
    </div>
  );
}

export default Clockin_int;
