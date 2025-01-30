import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import DatePicker from "react-datepicker";
import { LS } from "../../Utils/Resuse";
import "react-datepicker/dist/react-datepicker.css";

const Leaveapproval = () => {
  const [leaveData, setLeaveData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedOption, setSelectedOption] = useState("Leave");
  const isManager= LS.get("position")==="Manager";
  const isAdmin= LS.get('isadmin')
  useEffect(() => {
    if(LS.get("department")=="HR"){
      fetch("http://127.0.0.1:8000/auto_approve_manager_leaves")
      .then(response => response.json())
      .then(data => console.log("Auto-approval triggered:", data))
      .catch(error => console.error("Error auto-approving manager leaves:", error));
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const formattedDate = formatDate(selectedDate);
        let endpoint = "";

        switch (selectedOption) {
          case "Leave":
            // endpoint = `http://127.0.0.1:8000/manager_leave_requests/?requestDate=${formattedDate}&selectedOption=Leave`;
            if(LS.get("isadmin")==true)
              
              endpoint=`http://127.0.0.1:8000/manager_leave_requests/?requestDate=${formattedDate}&selectedOption=Leave`;
              else if (LS.get("position")=="Manager")
              endpoint = `http://127.0.0.1:8000/only_users_leave_requests/?requestDate=${formattedDate}&selectedOption=Leave&TL=string`;
                         //http://127.0.0.1:8000/only_users_leave_requests/?requestDate=2025-01-28&selectedOption=Leave&TL=string
              else if (LS.get("department")=="HR")
                endpoint=`http://127.0.0.1:8000/all_users_leave_requests/?requestDate=${formattedDate}&selectedOption=Leave`;
            break;
          case "LOP":
            endpoint = `http://127.0.0.1:8000/user_leave_requests/?requestDate=${formattedDate}&selectedOption=LOP`;
            break;
          case "Permission":
            endpoint = `http://127.0.0.1:8000/user_leave_requests/?requestDate=${formattedDate}&selectedOption=Permission`;
            break;
          default:
            break;
        }

        const response = await axios.get(endpoint);
        const leaveData =
          response.data && Array.isArray(response.data.user_leave_requests)
            ? response.data.user_leave_requests
            : [];
        console.log(leaveData);
        setLeaveData(leaveData);
        setLoading(false);
        setError(null);
      } catch (error) {
        setLoading(false);
        setLeaveData([]);
        setError("Error fetching data");
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

  const onRecommand = async (leave_id) => {
    try {
      console.log("Approve button clicked");
      console.log("Leave ID:", leave_id);
      const formData = new FormData();
      formData.append("status", "Recommend");
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
            return { ...row, status: "Recommend" };
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

  const onDisRecommand = async (leave_id) => {
    try {
      console.log("Disapprove button clicked");
      console.log("Leave ID:", leave_id);

      const formData = new FormData();
      formData.append("status", "Not_Recommend");
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
            return { ...row, status: "Not_Recommend" };
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
  <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback  ml-10 rounded-md">
      <div className="">
        <div className="flex justify-between border-b-2">
          <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text">
            Leave Request Approvals
          </h1>
          { isAdmin ?(
             <Link to="/admin/leave">
             <div className="">
               <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
                 Back
               </button>
             </div>
           </Link>): (

          <Link to="/User/LeaveManage">
          <div className="">
          <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
              Back
          </button>
          </div>
          </Link>
            
           )
          }
          
        </div>
        <div className="w-full bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2 mt-10">
          <header className="flex justify-between px-5 py-4 border-b border-gray-200">
            <DatePicker
              selected={selectedDate}
              onChange={(date) => setSelectedDate(date)}
              dateFormat="dd-MM-yyyy"
              className="border border-gray-300 rounded-md w-24 px-2 py-1 text-sm text-center"
              style={{ backgroundColor: "#f7fafc", cursor: "pointer" }}
              placeholderText="Select date"
              minDate={new Date("01-01-2024")}
              maxDate={new Date("31-12-2030")}
            />
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
                {renderTableHeader()}
                <tbody className="text-sm">
                  {loading ? (
                    <tr>
                      <td
                        colSpan="7"
                        className="p-2 whitespace-nowrap font-inter text-center"
                      >
                        <div className="font-medium text-center">
                          Loading...
                        </div>
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
                        
                          {
                            


                        selectedOption === "Leave" ? (
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
) :  (
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
                        ) }
                        <td className="p-2 whitespace-normal w-fit">
                          <div className="font-medium text-start w-fit">
                            {row.reason}
                          </div>
                        </td>
                        <td className="p-2  whitespace-normal w-fit">
                         
                          {
                             LS.get("department")=="HR" ?(
                              row.status === "Approved" ? (
                                <p className="text-green-500 font-inter text-start">
                                  Approved
                                </p>
                              ) : row.status === "Rejected" ? (
                                <p className="text-red-500 font-inter text-start">
                                  Rejected
                                </p>
                              ) : (
                                
                              
                                <div className="flex justify-start">
                                  <div
                                    style={{ backgroundColor: "#34D399" }}
                                    className="h-8 rounded-full p-1 mr-1"
                                  >
                                    
                                    <button
                                      onClick={() => onApprove(row.id)}
                                      className="text-white"
                                    >
                                      <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-6 w-6"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                      >
                                        <path
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                          strokeWidth={2}
                                          d="M5 13l4 4L19 7"
                                        />
                                      </svg>
                                    </button>
                                  </div>
                                  
                                  <div
                                    style={{ backgroundColor: "#EF4444" }}
                                    className="h-8 rounded-full p-1"
                                  >
                                  
                                    <button
                                      onClick={() => onDisapprove(row.id)}
                                      className="text-white"
                                    >
    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-6 w-6"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                      >
                                        <path
                                          strokeLinecap="round"
                                          strokeLinejoin="round"
                                          strokeWidth={2}
                                          d="M6 18L18 6M6 6l12 12"
                                        />
                                      </svg>
                                    </button>
                                  </div>
                                </div>
                              ) 
                              )
                            : LS.get("position")=="Manager" ?(
                              row.status === "Recommend" ? (
                                <p className="text-green-500 font-inter text-start">
                                  Recommend
                                </p>
                              ) : row.status === "Not_Recommend" ? (
                                <p className="text-red-500 font-inter text-start">
                                  Not Recommend
                                </p>
                              ) : (

                              <div className="flex justify-start">
                              <div
                                style={{ backgroundColor: "#34D399" }}
                                className="h-8 rounded-full p-1 mr-1"
                              >
                                
                                <button
                                  onClick={() => onRecommand(row.id)}
                                  className="text-white"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-check-fill" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M15.854 5.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 0 1 .708-.708L12.5 7.793l2.646-2.647a.5.5 0 0 1 .708 0"/>
  <path d="M1 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/>
</svg>
                                </button>
                              </div>
                              
                              <div
                                style={{ backgroundColor: "#EF4444" }}
                                className="h-8 rounded-full p-1"
                              >
                              
                                <button
                                  onClick={() => onDisRecommand(row.id)}
                                  className="text-white"
                                >
                                  
                                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill-slash" viewBox="0 0 16 16">
  <path d="M13.879 10.414a2.501 2.501 0 0 0-3.465 3.465zm.707.707-3.465 3.465a2.501 2.501 0 0 0 3.465-3.465m-4.56-1.096a3.5 3.5 0 1 1 4.949 4.95 3.5 3.5 0 0 1-4.95-4.95ZM11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0m-9 8c0 1 1 1 1 1h5.256A4.5 4.5 0 0 1 8 12.5a4.5 4.5 0 0 1 1.544-3.393Q8.844 9.002 8 9c-5 0-6 3-6 4"/>
</svg>
                                </button>
                              </div>
                            </div>
                              )
                            ): isAdmin &&(
                              row.status === "Recommend" ? (
                                <p className="text-green-500 font-inter text-start">
                                  Recommend
                                </p>
                              ) : row.status === "Not_Recommend" ? (
                                <p className="text-red-500 font-inter text-start">
                                  Not Recommend
                                </p>
                              ) : (

                              <div className="flex justify-start">
                              <div
                                style={{ backgroundColor: "#34D399" }}
                                className="h-8 rounded-full p-1 mr-1"
                              >
                                
                                <button
                                  onClick={() => onRecommand(row.id)}
                                  className="text-white"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-check-fill" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M15.854 5.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 0 1 .708-.708L12.5 7.793l2.646-2.647a.5.5 0 0 1 .708 0"/>
  <path d="M1 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/>
</svg>
                                </button>
                              </div>
                              
                              <div
                                style={{ backgroundColor: "#EF4444" }}
                                className="h-8 rounded-full p-1"
                              >
                              
                                <button
                                  onClick={() => onDisRecommand(row.id)}
                                  className="text-white"
                                >
                                  
                                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill-slash" viewBox="0 0 16 16">
  <path d="M13.879 10.414a2.501 2.501 0 0 0-3.465 3.465zm.707.707-3.465 3.465a2.501 2.501 0 0 0 3.465-3.465m-4.56-1.096a3.5 3.5 0 1 1 4.949 4.95 3.5 3.5 0 0 1-4.95-4.95ZM11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0m-9 8c0 1 1 1 1 1h5.256A4.5 4.5 0 0 1 8 12.5a4.5 4.5 0 0 1 1.544-3.393Q8.844 9.002 8 9c-5 0-6 3-6 4"/>
</svg>
                                </button>
                              </div>
                            </div>
                            )
                          )

                          }
                        </td>

                        
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="p-2 whitespace-nowrap">
                        <div className="font-medium text-center">No data available</div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="mt-2 flex justify-between items-center">
          <div>
            <button
              className="py-1 px-3 bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter rounded-full shadow-lg mr-2"
              onClick={() => paginate(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <button
              className="py-1 px-3 bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter rounded-full shadow-lg"
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
    </div>
  );
};

export default Leaveapproval;
