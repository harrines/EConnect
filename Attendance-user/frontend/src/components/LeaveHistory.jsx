// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import { Link } from "react-router-dom";
// import { LS } from "../Utils/Resuse";

// const LeaveHistory = () => {
//   const [leaveHistory, setLeaveHistory] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [currentPage, setCurrentPage] = useState(1);
//   const [itemsPerPage, setItemsPerPage] = useState(5);

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const userid = LS.get("userid");
//         const leaveResponse = await axios.get(
//           `http://127.0.0.1:8000/leave-History/${userid}`
//         );
//         console.log("API Response:", leaveResponse.data);
//         setLeaveHistory(
//           leaveResponse.data && Array.isArray(leaveResponse.data.leave_History)
//             ? leaveResponse.data.leave_History
//             : []
//         );
//         setLoading(false);
//         setError(null);
//       } catch (error) {
//         console.error("Error fetching data:", error);
//         setLoading(false);
//         setLeaveHistory([]);
//         setError("Error fetching data. Please try again later.");
//       }
//     };

//     fetchData();
//   }, []);

//   const indexOfLastItem = currentPage * itemsPerPage;
//   const indexOfFirstItem = indexOfLastItem - itemsPerPage;
//   const currentItems = leaveHistory.slice(indexOfFirstItem, indexOfLastItem);

//   const paginate = (pageNumber) => setCurrentPage(pageNumber);

//   return (
//     <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback">
//       <h1 className="text-5xl font-semibold font-poppins pb-4 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text">
//         Leave Management
//       </h1>
//       <div className="flex justify-end mb-4">
//         {/* <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
//             Leave Details
//           </h3> */}
//         <Link to="/User/Leave">
//           <div className="">
//             <button className=" mr-3 px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
//               Go Back
//             </button>
//           </div>
//         </Link>

//         <Link to="/User/Remote_details">
//           <div className="">
//             <button className="px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
//               Remote Details
//             </button>
//           </div>
//         </Link>
//       </div>
//       <div className="my-2">
//         <div className="border p-4 rounded-lg shadow-xl">
//           <h2 className="text-lg font-semibold mb-4 font-poppins">
//             Leave History
//           </h2>
//           {loading ? (
//             <p>Loading...</p>
//           ) : error ? (
//             <p>{error}</p>
//           ) : leaveHistory && leaveHistory.length > 0 ? (
//             <div className="overflow-x-auto">
//               <table className="w-full text-left text-sm text-gray-500">
//                 <thead className="text-xs text-black uppercase bg-[#6d9eeb7a]">
//                   <tr>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Date
//                     </th>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Employee ID
//                     </th>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Employee Name
//                     </th>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Leave Type
//                     </th>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Reason
//                     </th>
//                     <th scope="col" className="p-2 font-poppins text-center">
//                       Status
//                     </th>
//                   </tr>
//                 </thead>
//                 <tbody className=" text-gray-700 bg-white text-sm divide-y divide-gray-100">
//                   {currentItems.map((leave, index) => (
//                     <tr key={index}>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.selectedDate}
//                       </td>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.Employee_ID}
//                       </td>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.employeeName}
//                       </td>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.leaveType}
//                       </td>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.reason}
//                       </td>
//                       <td scope="col" className="p-2 font-poppins text-center">
//                         {leave.status}
//                       </td>
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>
//           ) : (
//             <p className="text-sm italic font-poppins">No records found</p>
//           )}
//         </div>
//         <div className="mt-2 flex justify-between items-center">
//           <div>
//             <button
//               className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white mr-2"
//               onClick={() => paginate(currentPage - 1)}
//               disabled={currentPage === 1}
//             >
//               Previous
//             </button>
//             <button
//               className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white"
//               onClick={() => paginate(currentPage + 1)}
//               disabled={indexOfLastItem >= leaveHistory.length}
//             >
//               Next
//             </button>
//           </div>
//           <div className="text-sm font-semibold text-gray-800">
//             {/* Page {currentPage} of {Math.ceil(filteredAttendanceData.length / itemsPerPage)} */}
//             Page {leaveHistory.length > 0 ? currentPage : 0} of{" "}
//             {leaveHistory.length > 0
//               ? Math.ceil(leaveHistory.length / itemsPerPage)
//               : 0}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default LeaveHistory;


import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { LS } from "../Utils/Resuse";
import axios from "axios";
import DatePicker from "react-datepicker"; // Import DatePicker

const LeaveHistory = () => {
  const [leaveData, setLeaveData] = useState([]); // Changed from leaveHistory
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [selectedOption, setSelectedOption] = useState("Leave");
  const [selectedDate, setSelectedDate] = useState(new Date()); // Added selectedDate

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const userid = LS.get("userid");
        const formattedDate = formatDate(selectedDate);
        let endpoint = "";

        switch (selectedOption) {
          case "Leave":
            endpoint = `http://127.0.0.1:8000/leave-History/${userid}/?selectedOption=Leave`;
            break;
          case "LOP":
            endpoint = `http://127.0.0.1:8000/Other-leave-history/${userid}/?selectedOption=LOP`;
            break;
          case "Permission":
            endpoint = `http://127.0.0.1:8000/Permission-history/${userid}/?selectedOption=Permission`;
            break;
          default:
            break;
        }

        const leaveResponse = await axios.get(endpoint); // Fixed endpoint
        console.log("API Response:", leaveResponse.data);
        setLeaveData(
          leaveResponse.data && Array.isArray(leaveResponse.data.leave_history)
            ? leaveResponse.data.leave_history
            : []
        );
        setLoading(false);
        setError(null);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
        setLeaveData([]);
        setError("Error fetching data. Please try again later.");
      }
    };

    fetchData();
  }, [selectedDate, selectedOption]);

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const renderTableHeader = () => {
    switch (selectedOption) {
      case "Leave":
        return (
          <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
            <tr>
              <th className="p-2 whitespace-nowrap text-start">S.No</th>
              <th className="p-2 whitespace-nowrap text-start">Employee ID</th>
              <th className="p-2 whitespace-nowrap text-start">Name</th>
              <th className="p-2 whitespace-nowrap text-start">Leave Type</th>
              <th className="p-2 whitespace-nowrap text-start">Date</th>
              <th
                className="p-2 whitespace-nowrap text-start"
                style={{ width: "30%" }}
              >
                Reason
              </th>
              <th className="p-2 whitespace-nowrap text-start">Status</th>
            </tr>
          </thead>
        );
      case "LOP":
        return (
          <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
            <tr>
              <th className="p-2 whitespace-nowrap text-start">S.No</th>
              <th className="p-2 whitespace-nowrap text-start">EMPLOYEE ID</th>
              <th className="p-2 whitespace-nowrap text-start">NAME</th>
              <th className="p-2 whitespace-nowrap text-start">FROM DATE</th>
              <th className="p-2 whitespace-nowrap text-start">TO DATE</th>
              <th
                className="p-2 whitespace-nowrap text-start"
                style={{ width: "30%" }}
              >
                REASON
              </th>
              <th className="p-2 whitespace-nowrap text-start">STATUS</th>
            </tr>
          </thead>
        );
      case "Permission":
        return (
          <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
            <tr>
              <th className="p-2 whitespace-nowrap text-start">S.No</th>
              <th className="p-2 whitespace-nowrap text-start">EMPLOYEE ID</th>
              <th className="p-2 whitespace-nowrap text-start">NAME</th>
              <th className="p-2 whitespace-nowrap text-start">DATE</th>
              <th className="p-2 whitespace-nowrap text-start">TIME</th>
              <th
                className="p-2 whitespace-nowrap text-start"
                style={{ width: "30%" }}
              >
                REASON
              </th>
              <th className="p-2 whitespace-nowrap text-start">STATUS</th>
            </tr>
          </thead>
        );
      default:
        return null;
    }
  };
  const onApprove = async (leave_id) => {
    try {
      console.log("Approve button clicked");
      console.log("Leave ID:", leave_id);
      const formData = new FormData();
      formData.append("status", "Approved");
      formData.append("leave_id", leave_id);

      console.log("FormData:", formData);

      const response = await axios.put(
        `http://127.0.0.1:8000/updated_user_leave_requests`,
        formData
      );
      console.log("API Response:", response.data);

      if (response.data.message === "Status updated successfully") {
        const updatedData = leaveData.map((row) => {
          if (row.id === leave_id) {
            return { ...row, status: "Approved" };
          }

          return row;
        });
        console.log(updatedData);
        setLeaveData(updatedData);
      } else {
        console.error(
          "No records found for the given userid, requestDate, or the status is already updated"
        );
      }
    } catch (error) {
      console.error("Error updating status:", error);
    }
  };

  const onDisapprove = async (leave_id) => {
    try {
      console.log("Disapprove button clicked");
      console.log("Leave ID:", leave_id);

      const formData = new FormData();
      formData.append("status", "Rejected");
      formData.append("leave_id", leave_id);

      console.log("FormData:", formData);

      const response = await axios.put(
        `http://127.0.0.1:8000/updated_user_leave_requests`,
        formData
      );
      console.log("API Response:", response.data);

      if (response.data.message === "Status updated successfully") {
        const updatedData = leaveData.map((row) => {
          if (row.id === leave_id) {
            return { ...row, status: "Rejected" };
          }
          return row;
        });
        setLeaveData(updatedData);
      } else {
        console.error(
          "No records found for the given userid, requestDate, or the status is already updated"
        );
      }
    } catch (error) {
      console.error("Error updating status:", error);
    }
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = leaveData.slice(indexOfFirstItem, indexOfLastItem);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md">
      <div className="flex justify-between border-b-2">
      <h1 className="text-5xl font-semibold font-poppins pb-4 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text ">
        Leave Management
      </h1>
      <div className="flex justify-end my-4">
        {/* <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
            Leave Details
          </h3> */}
        <Link to="/User/Leave">
          <div className="">
            <button className="mr-3 px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black active:bg-white active:text-white">
              Go Back
            </button>
          </div>
        </Link>

        <Link to="/User/Remote_details">
          <div className="">
            <button className="px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
              Remote Details
            </button>
          </div>
        </Link>
      </div>
      </div>
      {/* Date Picker and Select */}
      <div className="w-full bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2 mt-10">
        {/* Date Picker and Select */}
        <header className="flex justify-between px-5 py-4 border-b border-gray-200">
          {/* <DatePicker
              selected={selectedDate}
              onChange={(date) => setSelectedDate(date)}
              dateFormat="dd-MM-yyyy"
              className="border border-gray-300 rounded-md w-24 px-2 py-1 text-sm text-center"
              style={{ backgroundColor: "#f7fafc", cursor: "pointer" }}
              placeholderText="Select date"
              minDate={new Date("01-01-2024")}
              maxDate={new Date("31-12-2030")}
            /> */}
          <select
            className="border border-gray-300 rounded-md w-32 px-2 py-1 text-sm"
            onChange={(e) => setSelectedOption(e.target.value)}
            value={selectedOption}
          >
            <option value="Leave">Leave</option>
            <option value="LOP">LOP</option>
            <option value="Permission">Permission</option>
          </select>
        </header>
        <div className="p-3">
          <div>
            <table className="table-auto w-full overflow-y-auto">
              {/* Table Header */}
              {renderTableHeader()}
              <tbody className="text-sm">
                {loading ? (
                  <tr>
                    <td
                      colSpan="7"
                      className="p-2 whitespace-nowrap font-inter text-center"
                    >
                      <div className="font-medium text-center">Loading...</div>
                    </td>
                  </tr>
                ) : currentItems.length > 0 ? (
                  currentItems.map((row, index) => (
                    <tr key={index}>
                      <td className="p-2 whitespace-nowrap w-fit">
                        <div className="font-medium text-start w-fit">
                          {(currentPage - 1) * itemsPerPage + index + 1}.
                        </div>
                      </td>
                      {selectedOption === "Leave" ? (
                        <>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.Employee_ID}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap">
                            <div className="font-medium text-start w-fit">
                              {row.employeeName}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.leaveType}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.selectedDate}
                            </div>
                          </td>
                        </>
                      ) : selectedOption === "LOP" ? (
                        <>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.Employee_ID}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap">
                            <div className="font-medium text-start w-fit">
                              {row.employeeName}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.selectedDate}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.ToDate}
                            </div>
                          </td>
                        </>
                      ) : (
                        <>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.Employee_ID}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap">
                            <div className="font-medium text-start w-fit">
                              {row.employeeName}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.requestDate}
                            </div>
                          </td>
                          <td className="p-2 whitespace-nowrap w-fit">
                            <div className="font-medium text-start w-fit">
                              {row.timeSlot}
                            </div>
                          </td>
                        </>
                      )}
                      <td className="p-2 whitespace-normal w-fit">
                        <div className="font-medium text-start w-fit">
                          {row.reason}
                        </div>
                      </td>
                      {row.status? (
                        <td className="p-2 whitespace-normal w-fit">
                        <div className="font-medium text-start w-fit">
                          {row.status}
                        </div>
                      </td>
                      ):(
                        <td className="p-2 whitespace-normal w-fit">
                        <div className="font-medium text-start w-fit">
                          Pending
                        </div>
                      </td>
                      )}

                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">
                        No data available
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      {/* Pagination */}
      <div className="mt-2 flex justify-between items-center">
        <div>
          <button
            className="py-1 px-3 bg-blue-500 hover:bg-[#b7c6df80] hover:text-black text-white text-sm font-inter rounded-md shadow-lg mr-2"
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <button
            className="py-1 px-3 bg-blue-500 hover:bg-[#b7c6df80] hover:text-black text-white text-sm font-inter rounded-md shadow-lg"
            onClick={() => paginate(currentPage + 1)}
            disabled={indexOfLastItem >= leaveData.length}
          >
            Next
          </button>
        </div>
        <div className="text-sm font-semibold text-gray-800">
          Page {leaveData.length > 0 ? currentPage : 0} of{" "}
          {leaveData.length > 0
            ? Math.ceil(leaveData.length / itemsPerPage)
            : 0}
        </div>
      </div>
    </div>
  );
};

export default LeaveHistory;
