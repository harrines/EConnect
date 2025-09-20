import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Datetime from "react-datetime";
import "react-datetime/css/react-datetime.css";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Baseaxios, LS ,ipadr} from "../Utils/Resuse";
import moment from "moment";

const WorkFromHome = () => {
  const [fromDate, setFromDate] = useState(null);
  const [toDate, setToDate] = useState(null);
  const [reason, setReason] = useState("");
  const [ip, setip] = useState("");
  const [isApplying, setIsApplying] = useState(false);
  const [ipAddresses, setIpAddresses] = useState(null);
  const [selectedIp, setSelectedIp] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchIpAddresses();
  }, []);

  const fetchIpAddresses = async () => {
    try {
      const response = await fetch(`${ipadr}/ip-info`);
      const data = await response.json();
      setIpAddresses({
        public: data.public_ip,
        local: data.local_ip
      });
      setIsLoading(false);
    } catch (error) {
      console.error("Error fetching IP addresses:", error);
      toast.error("Failed to fetch IP addresses");
      setIsLoading(false);
    }
  };

  const handleFromDateChange = (date) => {
    setFromDate(date);
  };

  const handleToDateChange = (date) => {
    setToDate(date);
  };

  const handleIpChange = (e) => {
    setSelectedIp(e.target.value);
  };

  const remoteworkrequestapi = (newRequest) => {
    setIsApplying(true);
    const userid = LS.get("userid");
    const employeeName = LS.get("name");
  
    console.log("Sending Request Data:", { userid, employeeName, ...newRequest });
  
    Baseaxios.post("/remote-work-request", {
      userid,
      employeeName,
      ...newRequest,
    })
      .then((response) => {
        console.log("Response:", response);
        setIsApplying(false);
        if (response.data.message === "Remote work request stored successfully") {
          toast.success(response.data.result);
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        } else {
          toast.warning(response.data.result);
        }
      })
      .catch((err) => {
        setIsApplying(false);
        toast.error("Failed to submit remote work request");
        console.error("Error submitting remote work request:", err.response || err);
      });
  };

  const handleApplyButtonClick = () => {
    if (fromDate && toDate && reason && ip) {
      const newRequest = {
        fromDate: moment(fromDate).format("YYYY-MM-DD"),
        toDate: moment(toDate).format("YYYY-MM-DD"),
        requestDate: moment().toISOString().split('T')[0],
        reason: reason,
        ip: ip
      };
      remoteworkrequestapi(newRequest);
    } else {
      toast.error("Please fill in all fields including IP selection.", {
        position: "top-right",
      });
    }
  };

  const handleCancel = () => {
    setFromDate(null);
    setToDate(null);
    setReason("");
    setSelectedIp("");
  };

  const isWeekday = (date) => {
    return date.day() !== 0;
  };

  const isValidDate = (current) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return current.isSameOrAfter(today) && current.day() !== 0;
  };

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md">
      <h1 className="text-5xl font-semibold font-poppins pb-4 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
        Leave Management
      </h1>
      <div className="flex justify-between mt-3">
        <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
          Work from home
        </h3>
        <Link to="/User/Leave">
          <div className="">
            <button className="px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
              Go Back
            </button>
          </div>
        </Link>
      </div>
      <div className="mt-10">
        <div className="mt-4 bg-gradient-to-tr from-white to-blue-100 border-x p-4 rounded-lg shadow-xl">
          <div className="container mx-auto">
            <form>
              <div className="">
                <label
                  htmlFor="fromDate"
                  className="block text-base font-medium text-gray-700 mb-2"
                >
                  From Date
                </label>
                <Datetime
                  id="fromDate"
                  dateFormat="DD-MM-YYYY"
                  timeFormat={false}
                  value={fromDate}
                  onChange={handleFromDateChange}
                  isValidDate={(current) =>
                    isWeekday(current) && isValidDate(current)
                  }
                  inputProps={{
                    className:
                      "p-2 text-sm border border-gray-300 rounded-md block w-full",
                    placeholder: "Select from date",
                  }}
                />
              </div>
              <div className="mt-4">
                <label
                  htmlFor="toDate"
                  className="block text-base font-medium text-gray-700 mb-2"
                >
                  To Date
                </label>
                <Datetime
                  id="toDate"
                  dateFormat="DD-MM-YYYY"
                  timeFormat={false}
                  value={toDate}
                  onChange={handleToDateChange}
                  isValidDate={(current) =>
                    isWeekday(current) && isValidDate(current)
                  }
                  inputProps={{
                    className:
                      "p-2 text-sm border border-gray-300 rounded-md block w-full",
                    placeholder: "Select to date",
                  }}
                  minDate={
                    fromDate
                      ? moment(fromDate).add(1, "days").format("YYYY-MM-DD")
                      : undefined
                  }
                />
              </div>
              <div className="mt-4">
                <label
                  htmlFor="ipSelect"
                  className="block text-base font-medium text-gray-700 mb-2"
                >
                  Select IP Address
                </label>
                {/* <select
                  id="ipSelect"
                  value={selectedIp}
                  onChange={handleIpChange}
                  className="p-2 text-sm border border-gray-300 rounded-md block w-full"
                  disabled={isLoading}
                >
                  <option value="">Select an IP address</option>
                  {ipAddresses && (
                    <>
                      <option value={ipAddresses.public}>
                        Public IP: {ipAddresses.public}
                      </option>
                      <option value={ipAddresses.local}>
                        Local IP: {ipAddresses.local}
                      </option>
                    </>
                  )}
                </select> */}
                <textarea
                  id="ip"
                  value={ip}
                  onChange={(e) => setip(e.target.value)}
                  rows={1}
                  className="mt-2 border border-gray-300 p-2 w-full font-poppins rounded-md text-sm"
                  placeholder="Enter IP address"
                />
              </div>
              <div className="mt-4">
                <label
                  htmlFor="reason"
                  className="block text-base font-medium text-gray-700"
                >
                  Reason
                </label>
                <textarea
                  id="reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={1}
                  className="mt-2 border border-gray-300 p-2 w-full font-poppins rounded-md text-sm"
                  placeholder="Enter reason"
                />
              </div>
              <button
                type="button"
                onClick={handleApplyButtonClick}
                className={`mt-4 px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black active:bg-white active:text-white ${
                  isApplying ? "opacity-50 cursor-not-allowed" : ""
                }`}
                disabled={isApplying}
              >
                {isApplying ? "Applying..." : "Apply"}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 ml-2 bg-gray-500 rounded-md hover:text-slate-900 hover:bg-[#b7c6df80] text-white"
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={1000}
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
};

export default WorkFromHome;