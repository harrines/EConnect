import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch, faDownload } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import * as XLSX from "xlsx";
import { Link } from "react-router-dom";
import { LS } from "../../Utils/Resuse";

const Leavehistory = () => {
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const isadmin =LS.get('isadmin');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `http://127.0.0.1:8000/leave-history`
        );
        const filteredData =
          response.data && Array.isArray(response.data.leave_history)
            ? response.data.leave_history.filter((item) =>
              item.employeeName
                .toLowerCase()
                .includes(searchTerm.toLowerCase())
            )
            : [];
        console.log("API Response:", response.data);
        setAttendanceData(filteredData); // Update with filtered data
        setLoading(false);
        setError(null);
      } catch (error) {
        console.error("Error fetching attendance data:", error);
        setLoading(false);
        setAttendanceData([]);
        setError("Error fetching data. Please try again."); // Update error state
      }
    };

    fetchData();
  }, [searchTerm]); // Trigger fetch whenever searchTerm changes

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = attendanceData.slice(indexOfFirstItem, indexOfLastItem);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const downloadExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(attendanceData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "LeaveHistoryData");
    XLSX.writeFile(workbook, "leave_history_data.xlsx");
  };

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback  ml-10 rounded-md ">
      <div className="">
      <div className="flex justify-between border-b-2">
        <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
          Leave History
        </h1>
        
        {
          isadmin ?(
            <Link to="/admin/leave">
                    <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
                      Back
                    </button>
                  </Link>
          ):(
            <Link to="/User/LeaveManage">
                    <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg">
                      Back
                    </button>
                  </Link>
          )
        }
        
        
                  </div>
        <div className="bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2 mt-10">
          <header className="px-4 py-4 border-b border-gray-200 flex justify-between">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name..."
                className="px-2 py-1 rounded-md border text-sm pl-8 border-gray-300 w-40"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <div className="absolute top-0 left-0 mt-1 ml-2 text-gray-400 cursor-text">
                <FontAwesomeIcon icon={faSearch} />
              </div>
            </div>
          </header>
          <div className="p-3">
            <div>
              {error && <p className="text-red-500">{error}</p>}
              <table className="table-auto w-full overflow-y-auto">
                <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
                  <tr>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">S.No</div>
                    </th>
                    <th className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">
                        Employee ID
                      </div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Name</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">
                        Leave Type
                      </div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Date</div>
                    </th>
                  </tr>
                </thead>

                <tbody className="text-sm">
                  {loading ? (
                    <tr>
                      <td
                        colSpan="4"
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
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {index + 1 + (currentPage - 1) * itemsPerPage}.
                          </div>
                        </td>
                        <td className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {row.Employee_ID}
                          </div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {row.employeeName}
                          </div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {row.leaveType}
                          </div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {row.selectedDate}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="p-2 whitespace-nowrap">
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
              disabled={indexOfLastItem >= attendanceData.length}
            >
              Next
            </button>
          </div>
          <div className="text-sm font-semibold text-gray-800">
            {/* Page {currentPage} of {Math.ceil(attendanceData.length / itemsPerPage)} */}
            Page {attendanceData.length > 0 ? currentPage : 0} of{" "}
            {attendanceData.length > 0
              ? Math.ceil(attendanceData.length / itemsPerPage)
              : 0}
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            className="py-1 px-3 bg-blue-500 hover:bg-blue-400 text-white text-sm font-inter rounded-full shadow-lg"
            onClick={downloadExcel}
          >
            <FontAwesomeIcon icon={faDownload} /> Download
          </button>
        </div>
      </div>
    </div>
  );
};

export default Leavehistory;













// import React, { useState, useEffect } from "react";
// import Sidebar from "./Sidebar.jsx";
// import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { faSearch } from "@fortawesome/free-solid-svg-icons";
// import axios from "axios";

// const Leavehistory = () => {
//   const [attendanceData, setAttendanceData] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [searchTerm, setSearchTerm] = useState("");
//   const [currentPage, setCurrentPage] = useState(1);
//   const [itemsPerPage, setItemsPerPage] = useState(5);

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         setLoading(true);
//         const response = await axios.get(
//           // `https://192.168.123.247:8000/leave-history`
//           `http://127.0.0.1:8000/leave-history`
//         );
//         const filteredData =
//           response.data && Array.isArray(response.data.leave_history)
//             ? response.data.leave_history.filter((item) =>
//                 item.employeeName
//                   .toLowerCase()
//                   .includes(searchTerm.toLowerCase())
//               )
//             : [];
//         console.log("API Response:", response.data);
//         setAttendanceData(filteredData); // Update with filtered data
//         setLoading(false);
//         setError(null);
//       } catch (error) {
//         console.error("Error fetching attendance data:", error);
//         setLoading(false);
//         setAttendanceData([]);
//         setError("Error fetching data. Please try again."); // Update error state
//       }
//     };

//     fetchData();
//   }, [searchTerm]); // Trigger fetch whenever searchTerm changes

//   const indexOfLastItem = currentPage * itemsPerPage;
//   const indexOfFirstItem = indexOfLastItem - itemsPerPage;
//   const currentItems = attendanceData.slice(indexOfFirstItem, indexOfLastItem);

//   const paginate = (pageNumber) => setCurrentPage(pageNumber);

//   return (
//     <div className="flex bg-[#6d9eeb] bg-gradient-to-b from-blue-400 to-indigo-800">
//       <Sidebar />
//       <div className="container my-6 mx-6 bg-white rounded-3xl p-10">
//         <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text">
//           Leave History
//         </h1>
//         <div className="bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2">
//           <header className="px-4 py-4 border-b border-gray-200 flex justify-between">
//             <div className="relative">
//               <input
//                 type="text"
//                 placeholder="Search by name..."
//                 className="px-2 py-1 rounded-md border text-sm pl-8 border-gray-300 w-40"
//                 value={searchTerm}
//                 onChange={(e) => setSearchTerm(e.target.value)}
//               />
//               <div className="absolute top-0 left-0 mt-1 ml-2 text-gray-400 cursor-text">
//                 <FontAwesomeIcon icon={faSearch} />
//               </div>
//             </div>
//           </header>
//           <div className="p-3">
//             <div>
//               {error && <p className="text-red-500">{error}</p>}
//               <table className="table-auto w-full overflow-y-auto">
//                 <thead className="text-sm font-semibold uppercase text-black bg-[#6d9eeb7a]">
//                   <tr>
//                     <th scope="col" className="p-2 whitespace-nowrap">
//                       <div className="font-semibold text-center">S.No</div>
//                     </th>
//                     <th className="p-2 whitespace-nowrap">
//                       <div className="font-semibold text-center">
//                         Employee ID
//                       </div>
//                     </th>
//                     <th scope="col" className="p-2 whitespace-nowrap">
//                       <div className="font-semibold text-center">Name</div>
//                     </th>
//                     <th scope="col" className="p-2 whitespace-nowrap">
//                       <div className="font-semibold text-center">
//                         Leave Type
//                       </div>
//                     </th>
//                     <th scope="col" className="p-2 whitespace-nowrap">
//                       <div className="font-semibold text-center">Date</div>
//                     </th>
//                   </tr>
//                 </thead>

//                 <tbody className="text-sm">
//                   {loading ? (
//                     <tr>
//                       <td
//                         colSpan="4"
//                         className="p-2 whitespace-nowrap font-inter text-center"
//                       >
//                         <div className="font-medium text-center">
//                           Loading...
//                         </div>
//                       </td>
//                     </tr>
//                   ) : currentItems.length > 0 ? (
//                     currentItems.map((row, index) => (
//                       <tr key={index}>
//                         <td scope="col" className="p-2 whitespace-nowrap">
//                           <div className="font-medium text-center">
//                             {index + 1 + (currentPage - 1) * itemsPerPage}.
//                           </div>
//                         </td>
//                         <td className="p-2 whitespace-nowrap">
//                           <div className="font-medium text-center">
//                             {row.Employee_ID}
//                           </div>
//                         </td>
//                         <td scope="col" className="p-2 whitespace-nowrap">
//                           <div className="font-medium text-center">
//                             {row.employeeName}
//                           </div>
//                         </td>
//                         <td scope="col" className="p-2 whitespace-nowrap">
//                           <div className="font-medium text-center">
//                             {row.leaveType}
//                           </div>
//                         </td>
//                         <td scope="col" className="p-2 whitespace-nowrap">
//                           <div className="font-medium text-center">
//                             {row.selectedDate}
//                           </div>
//                         </td>
//                       </tr>
//                     ))
//                   ) : (
//                     <tr>
//                       <td colSpan="4" className="p-2 whitespace-nowrap">
//                         <div className="font-medium text-center">
//                           No data available
//                         </div>
//                       </td>
//                     </tr>
//                   )}
//                 </tbody>
//               </table>
//             </div>
//           </div>
//         </div>
//         <div className="mt-2 flex justify-between items-center">
//           <div>
//             <button
//               className="py-1 px-3 bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter rounded-full shadow-lg mr-2"
//               onClick={() => paginate(currentPage - 1)}
//               disabled={currentPage === 1}
//             >
//               Previous
//             </button>
//             <button
//               className="py-1 px-3 bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter rounded-full shadow-lg"
//               onClick={() => paginate(currentPage + 1)}
//               disabled={indexOfLastItem >= attendanceData.length}
//             >
//               Next
//             </button>
//           </div>
//           <div className="text-sm font-semibold text-gray-800">
//             {/* Page {currentPage} of {Math.ceil(attendanceData.length / itemsPerPage)} */}
//             Page {attendanceData.length > 0 ? currentPage : 0} of{" "}
//             {attendanceData.length > 0
//               ? Math.ceil(attendanceData.length / itemsPerPage)
//               : 0}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Leavehistory;



