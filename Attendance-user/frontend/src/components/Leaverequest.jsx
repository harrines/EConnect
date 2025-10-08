import React, { useState } from "react";
import Datetime from "react-datetime";
import "react-datetime/css/react-datetime.css";
import { Link } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Baseaxios, LS } from "../Utils/Resuse";
import moment from "moment";

const LeaveRequest = () => {
  const [leaveType, setLeaveType] = useState("");
  const [selectedDate, setSelectedDate] = useState(null);
  const [timeSlot, setTimeSlot] = useState("");
  const [reason, setReason] = useState("");
  const [validationMessage, setValidationMessage] = useState("");
  const [isApplying, setIsApplying] = useState(false);

  // State for "Other Leave"
  const [otherFromDate, setOtherFromDate] = useState(null);
  const [otherToDate, setOtherToDate] = useState(null);
  const [otherReason, setOtherReason] = useState("");

  // State for "Bonus Leave"
  const [bonusLeaveDate, setBonusLeaveDate] = useState(null);
  const [bonusLeaveReason, setBonusLeaveReason] = useState("");

  const handleLeaveTypeChange = (event) => {
    setLeaveType(event.target.value);
    setSelectedDate(null);
    setValidationMessage("");
  };

  const handleDateChange = (date) => {
    if (date && moment.isMoment(date)) {
      setSelectedDate(date);
    } else if (date instanceof Date && !isNaN(date.getTime())) {
      setSelectedDate(moment(date));
    } else {
      setSelectedDate(null);
    }
    setValidationMessage("");
  };

  const handleTimeSlotChange = (event) => {
    setTimeSlot(event.target.value);
    setValidationMessage("");
  };

  const handleReasonChange = (event) => {
    setReason(event.target.value);
    setValidationMessage("");
  };

  const handleOtherFromDateChange = (date) => {
    if (date && moment.isMoment(date)) setOtherFromDate(date);
    else if (date instanceof Date && !isNaN(date.getTime())) setOtherFromDate(moment(date));
    else setOtherFromDate(null);
    setValidationMessage("");
  };

  const handleOtherToDateChange = (date) => {
    if (date && moment.isMoment(date)) setOtherToDate(date);
    else if (date instanceof Date && !isNaN(date.getTime())) setOtherToDate(moment(date));
    else setOtherToDate(null);
    setValidationMessage("");
  };

  const handleOtherReasonChange = (event) => {
    setOtherReason(event.target.value);
    setValidationMessage("");
  };

  const handleCancel = () => {
    setLeaveType("");
    setSelectedDate(null);
    setReason("");
    setOtherFromDate(null);
    setOtherToDate(null);
    setOtherReason("");
    setTimeSlot("");
    setValidationMessage("");
    setIsApplying(false);
  };

  const leaverequestapi = (newLeave) => {
    setIsApplying(true);
    const userid = LS.get("user.userid");
    let time = new Date().toLocaleTimeString();

    let endpoint = "/leave-request";
    if (newLeave.leaveType === "Other Leave") endpoint = "/Other-leave-request";
    if (newLeave.leaveType === "Permission") endpoint = "/Permission-request";
    if (newLeave.leaveType === "Bonus Leave") endpoint = "/Bonus-leave-request";

    Baseaxios.post(endpoint, {
      userid,
      employeeName: LS.get("name"),
      time,
      ...newLeave,
      status: "",
    })
      .then((response) => {
        setIsApplying(false);
        const responseData = response.data;

        if (responseData.success !== undefined) {
          if (responseData.success) {
            toast.success(responseData.message || "Leave request submitted successfully");
            setTimeout(() => window.location.reload(), 2000);
          } else if (responseData.status === "conflict") {
            toast.warning(`📅 ${responseData.message}`, { autoClose: 6000, position: "top-center" });
            setTimeout(() => toast.info(`💡 ${responseData.suggestion}`, { autoClose: 5000, position: "top-center" }), 1000);
          } else if (responseData.status === "validation_error") {
            toast.error(`❌ ${responseData.details || responseData.message}`, { autoClose: 5000, position: "top-center" });
            setTimeout(() => toast.info(`💡 ${responseData.suggestion}`, { autoClose: 4000, position: "top-center" }), 1000);
          }
        } else {
          const resultMessage = responseData.result || responseData.message;
          if (resultMessage && typeof resultMessage === "string" && resultMessage.toLowerCase().includes("success")) {
            toast.success("Leave request submitted successfully");
            setTimeout(() => window.location.reload(), 2000);
          } else {
            toast.warning(resultMessage || "Leave request processed with conditions");
          }
        }
      })
      .catch((err) => {
        setIsApplying(false);
        let errorMessage = err.response?.data?.detail || err.response?.data?.result || err.response?.data?.message;

        if (errorMessage) {
          if (errorMessage.includes("Conflict") || errorMessage.includes("already has")) {
            toast.error(`⚠️ ${errorMessage}`, { autoClose: 5000, position: "top-center" });
            setTimeout(() => toast.info("💡 Tip: Check your leave history for this date", { autoClose: 4000, position: "top-center" }), 1000);
          } else if (errorMessage.includes("Sunday")) {
            toast.error("❌ Leave requests cannot be made for Sundays", { autoClose: 3000 });
          } else {
            toast.error(`❌ ${errorMessage}`, { autoClose: 4000 });
          }
        } else {
          toast.error("❌ Network error. Please check your connection and try again.", { autoClose: 3000 });
        }
      });
  };

  const handleApplyButtonClick = () => {
    if (!leaveType) setValidationMessage("Select a leave type");
    else if (leaveType === "Other Leave" && (!otherFromDate || !otherToDate || !otherReason.trim())) setValidationMessage("Complete all fields for Other Leave");
    else if (!selectedDate && (leaveType === "Sick Leave" || leaveType === "Casual Leave" || leaveType === "Bonus Leave")) setValidationMessage("Select a valid date");
    else if (!reason.trim() && (leaveType === "Sick Leave" || leaveType === "Casual Leave" || leaveType === "Bonus Leave")) setValidationMessage("Enter a valid reason");
    else if (leaveType === "Permission" && (!selectedDate || !timeSlot || !reason.trim())) setValidationMessage("Complete all fields for Permission");
    else {
      let newLeave;

      if (["Sick Leave", "Casual Leave", "Bonus Leave", "Permission"].includes(leaveType)) {
        const formattedSelectedDate = moment(selectedDate).format("YYYY-MM-DD");
        newLeave = {
          leaveType,
          selectedDate: formattedSelectedDate,
          reason,
          ...(leaveType === "Permission" && { timeSlot }),
          requestDate: new Date().toISOString().split("T")[0],
        };
      } else if (leaveType === "Other Leave") {
        const formattedFromDate = moment(otherFromDate).format("YYYY-MM-DD");
        const formattedToDate = moment(otherToDate).format("YYYY-MM-DD");
        newLeave = {
          leaveType,
          selectedDate: formattedFromDate,
          ToDate: formattedToDate,
          reason: otherReason,
          requestDate: new Date().toISOString().split("T")[0],
        };
      }

      leaverequestapi(newLeave);
    }
  };

  const isValidDate = (current) => {
    const date = current instanceof Date ? current : current.toDate();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return date.getDay() !== 0 && date >= today; // Disable Sundays and past dates
  };

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md">
      <h1 className="text-5xl font-semibold font-poppins pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
        Leave Management
      </h1>
      <div className="flex justify-between mt-3">
        <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
          Request a Leave
        </h3>
        <Link to="/User/Leave">
          <button className="p-2 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black active:bg-white active:text-white">
            Go Back
          </button>
        </Link>
      </div>

      <div className="mt-6 bg-gradient-to-tr from-white to-blue-100 border-x p-4 rounded-lg shadow-xl">
        <h2 className="text-sm font-semibold mb-2 font-poppins">Type of Leave</h2>
        <div className="flex flex-wrap mb-2">
          {["Sick Leave", "Casual Leave", "Other Leave", "Permission", "Bonus Leave"].map((type) => (
            <label key={type} className="inline-flex items-center mr-4 mb-2">
              <input type="radio" className="form-radio" value={type} checked={leaveType === type} onChange={handleLeaveTypeChange} />
              <span className="ml-2 font-poppins text-sm">{type}</span>
            </label>
          ))}
        </div>

        {(leaveType === "Sick Leave" || leaveType === "Casual Leave" || leaveType === "Permission" || leaveType === "Bonus Leave") && (
          <>
            <h2 className="text-sm font-semibold mb-2 font-poppins">Date</h2>
            <Datetime
              value={selectedDate}
              onChange={handleDateChange}
              dateFormat="DD-MM-YYYY"
              isValidDate={isValidDate}
              timeFormat={false}
              closeOnSelect
              inputProps={{ className: "p-2 text-sm border border-gray-300 rounded-md block w-full mb-2", placeholder: "Select date" }}
            />

            {leaveType === "Permission" && (
              <>
                <h2 className="text-sm font-semibold mb-2 font-poppins">Time Slot</h2>
                <div className="mb-2">
                  {["Forenoon", "Afternoon"].map((slot) => (
                    <label key={slot} className="inline-flex items-center mr-4">
                      <input type="radio" className="form-radio" value={slot} checked={timeSlot === slot} onChange={handleTimeSlotChange} />
                      <span className="ml-2 font-poppins text-sm">{slot}</span>
                    </label>
                  ))}
                </div>
              </>
            )}

            <h2 className="text-sm font-semibold mb-2 font-poppins">Reason</h2>
            <input type="text" className="border border-gray-300 p-2 w-full font-poppins rounded-lg text-sm" placeholder="Enter reason" value={reason} onChange={handleReasonChange} />
          </>
        )}

        {leaveType === "Other Leave" && (
          <>
            <h2 className="text-sm font-semibold mb-2 font-poppins">From Date</h2>
            <Datetime value={otherFromDate} onChange={handleOtherFromDateChange} dateFormat="DD-MM-YYYY" isValidDate={isValidDate} timeFormat={false} closeOnSelect inputProps={{ className: "p-2 text-sm border border-gray-300 rounded-md block w-full mb-2", placeholder: "Select from date" }} />

            <h2 className="text-sm font-semibold mb-2 font-poppins">To Date</h2>
            <Datetime value={otherToDate} onChange={handleOtherToDateChange} dateFormat="DD-MM-YYYY" isValidDate={isValidDate} timeFormat={false} closeOnSelect inputProps={{ className: "p-2 text-sm border border-gray-300 rounded-md block w-full mb-2", placeholder: "Select to date" }} />

            <h2 className="text-sm font-semibold mb-2 font-poppins">Reason</h2>
            <input type="text" className="border border-gray-300 p-2 w-full font-poppins rounded-lg text-sm" placeholder="Enter reason" value={otherReason} onChange={handleOtherReasonChange} />
          </>
        )}

        {validationMessage && <p className="text-red-400 text-xs italic font-poppins mt-2">{validationMessage}</p>}

        <div className="mt-4">
          <button className={`p-2 mr-2 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black active:bg-white active:text-white ${isApplying ? "opacity-50 cursor-not-allowed" : ""}`} onClick={handleApplyButtonClick} disabled={isApplying}>
            {isApplying ? "Applying..." : "Apply"}
          </button>
          <button className="p-2 bg-gray-500 rounded-md hover:text-slate-900 text-white" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={2000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default LeaveRequest;
