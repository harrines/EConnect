import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { LS } from "../../Utils/Resuse";

const Wfh = () => {
  const [leaveData, setLeaveData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const isadmin=LS.get('isadmin');
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/remote_work_requests"
      );
      setLeaveData(response.data.remote_work_requests);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const updateStatus = async (userid, status) => {
    try {
      console.log("User ID:", userid, "Status:", status); // Debugging
      const formData = new FormData();
      formData.append("status", status);
      formData.append("userid", userid);

      await axios.put(
        `http://127.0.0.1:8000/updated_remote_work_requests`,
        formData
      );

      // Update status locally
      const updatedData = leaveData.map((row) => {
        if (row.id === userid) {
          return { ...row, status: status };
        }
        return row;
      });
      setLeaveData(updatedData);
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
      <div>
        <div className="flex justify-between border-b-2">
          <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text">
            Remote Work Approvals
          </h1>
          {
            isadmin ?(
              <Link to="/admin/leave">
              <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
                Back
              </button>
            </Link>
            ) :(
              <Link to="/User/leaveManage">
              <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
                Back
              </button>
            </Link>
            )
          }
          
        </div>
        <div className="w-full bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2 mt-10">
          <header className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-semibold text-gray-800">Remote Work Requests</h2>
          </header>
          <div className="p-3">
            <table className="table-auto w-full overflow-y-auto">
              <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
                <tr>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">S.No</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Employee ID</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Name</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">From Date</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">To Date</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Reason</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Status</div>
                  </th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {currentItems.map((row, index) => (
                  <tr key={index}>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">
                        {(currentPage - 1) * itemsPerPage + index + 1}.
                      </div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">{row.userid}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">{row.employeeName}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">{row.fromDate}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">{row.toDate}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="font-medium text-center">{row.reason}</div>
                    </td>
                    <td className="p-2">
                      {row.status === "Approved" ? (
                        <p className="text-green-500 font-inter text-center">Approved</p>
                      ) : row.status === "Rejected" ? (
                        <p className="text-red-500 font-inter text-center">Rejected</p>
                      ) : (
                        <div className="flex justify-center">
                          <button
                            style={{ backgroundColor: "#34D399" }}
                            className="h-8 w-8 rounded-full text-white mr-4"
                            onClick={() => updateStatus(row.userid, "Approved")}
                          >
                            ✓
                          </button>
                          <button
                            style={{ backgroundColor: "#EF4444" }}
                            className="h-8 w-8 rounded-full text-white"
                            onClick={() => updateStatus(row.userid, "Rejected")}
                          >
                            ✗
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="mt-2 flex justify-between items-center">
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
          <div className="text-sm font-semibold text-gray-800">
            Page {leaveData.length > 0 ? currentPage : 0} of{" "}
            {leaveData.length > 0 ? Math.ceil(leaveData.length / itemsPerPage) : 0}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Wfh;
