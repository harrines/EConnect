// import { Link } from "react-router-dom";
// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import { Baseaxios, LS } from "../Utils/Resuse";

// export default function Clockdashboard() {
//   const [attendanceData, setAttendanceData] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [selectedMonth, setSelectedMonth] = useState(""); // Set default month
//   const [selectedYear, setSelectedYear] = useState("");
//   const [currentPage, setCurrentPage] = useState(1);
//   const [itemsPerPage, setItemsPerPage] = useState(5);

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const userid = LS.get("userid");
//         console.log(userid)
//         const attendanceResponse = await axios.get(
//           `http://127.0.0.1:8000/clock-records/${userid}`
//         );
//         console.log("API Response:", attendanceResponse.data);
//         setAttendanceData(
//           attendanceResponse.data &&
//             Array.isArray(attendanceResponse.data.clock_records)
//             ? attendanceResponse.data.clock_records
//             : []
//         );
//         setLoading(false);
//         setError(null);
//       } catch (error) {
//         console.error("Error fetching data:", error);
//         setLoading(false);
//         setAttendanceData([]);
//       }
//     };

//     fetchData();
//   }, []);

//   useEffect(() => {
//     const currentDate = new Date();
//     const currentMonth = currentDate.toLocaleString("default", {
//       month: "long",
//     });
//     setSelectedMonth(currentMonth);
//   }, []); // Set default month to the current month when the component mounts

//   const months = [
//     "January",
//     "February",
//     "March",
//     "April",
//     "May",
//     "June",
//     "July",
//     "August",
//     "September",
//     "October",
//     "November",
//     "December",
//   ];

//   const years = ["2024"];

//   const handleMonthChange = (month) => {
//     setSelectedMonth(month);
//   };

//   const handleYearChange = (year) => {
//     setSelectedYear(year);
//   };

//   const filteredAttendanceData = attendanceData.filter((row) => {
//     const rowDate = new Date(row.date);
//     const monthMatch =
//       !selectedMonth || rowDate.getMonth() === months.indexOf(selectedMonth);
//     const yearMatch =
//       !selectedYear || rowDate.getFullYear() === parseInt(selectedYear);
//     return monthMatch && yearMatch;
//   });

//   // Pagination logic
//   const indexOfLastItem = currentPage * itemsPerPage;
//   const indexOfFirstItem = indexOfLastItem - itemsPerPage;
//   const currentItems = filteredAttendanceData.slice(
//     indexOfFirstItem,
//     indexOfLastItem
//   );

//   const paginate = (pageNumber) => setCurrentPage(pageNumber);
//   console.log('Filtered Data:', filteredAttendanceData);
//   return (
//     <div className="rounded-md w-full px-[7rem] my-4">
//       <div className="w-full h-full bg-whte shadow-lg rounded-md border border-gray-200">
//         <header className="px-5 py-4 border-b border-gray-200 flex justify-between items-center">
//           <h2 className="font-semibold text-gray-800">Timing</h2>
//           <div>
//             <select
//               className="border rounded-md p-1 mr-2 text-sm font-semibold text-gray-800"
//               onChange={(e) => handleMonthChange(e.target.value)}
//             >
//               <option className="font-semibold text-gray-800" value="">
//                 Months
//               </option>
//               {months.map((month, index) => (
//                 <option
//                   className="text-sm font-semibold text-gray-600"
//                   key={index}
//                   value={month}
//                 >
//                   {month}
//                 </option>
//               ))}
//             </select>
//             <select
//               className="border rounded-md p-1 text-sm font-semibold text-gray-800"
//               onChange={(e) => handleYearChange(e.target.value)}
//             >
//               <option className="font-semibold text-gray-800" value="">
//                 Years
//               </option>
//               {years.map((year, index) => (
//                 <option
//                   className="text-sm font-semibold text-gray-600"
//                   key={index}
//                   value={year}
//                 >
//                   {year}
//                 </option>
//               ))}
//             </select>
//           </div>
//         </header>
//         <div className="p-3">
//           <div>
//             <table className="table-auto w-full overflow-y-auto">
//               <thead className="text-xs font-semibold uppercase text-black bg-[#6d9eeb7a]">
//                 <tr>
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">Date</div>
//                   </th>
//                   {/* <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">employee ID</div>
//                   </th> */}
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">Login Time</div>
//                   </th>
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">Logout Time</div>
//                   </th>
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">
//                       Total hours of working
//                     </div>
//                   </th>
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">Status</div>
//                   </th>
//                   <th className="p-2 whitespace-nowrap">
//                     <div className="font-semibold text-center">Remark</div>
//                   </th>
//                 </tr>
//               </thead>
//               <tbody className="text-sm divide-y divide-gray-100">
//                 {currentItems.map((row, index) => (
//                   <tr key={index}>
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.date}</div>
//                     </td>
//                     {/* <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.Employee_ID}</div>
//                     </td> */}
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.clockin}</div>
//                     </td>
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.clockout}</div>
//                     </td>
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">
//                         {row.total_hours_worked}
//                       </div>
//                     </td>
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.status}</div>
//                     </td>
//                     <td className="p-2 whitespace-nowrap">
//                       <div className="text-center">{row.remark}</div>
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         </div>
//       </div>
//       <div className="mt-2 flex justify-between items-center">
//         <div>
//           <button
//             className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white mr-2"
//             onClick={() => paginate(currentPage - 1)}
//             disabled={currentPage === 1}
//           >
//             Previous
//           </button>
//           <button
//             className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white"
//             onClick={() => paginate(currentPage + 1)}
//             disabled={indexOfLastItem >= filteredAttendanceData.length}
//           >
//             Next
//           </button>
//         </div>
//         <div className="text-sm font-semibold text-gray-800">
//           Page {filteredAttendanceData.length > 0 ? currentPage : 0} of{" "}
//           {filteredAttendanceData.length > 0
//             ? Math.ceil(filteredAttendanceData.length / itemsPerPage)
//             : 0}
//         </div>
//       </div>
//     </div>
//   );
// }



import { Link } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { Baseaxios, LS } from "../Utils/Resuse";

export default function Clockdashboard() {
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedYear, setSelectedYear] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const requestOptions = {
        method: "GET",
        redirect: "follow"
      };

      try {
       const userId = LS.get("userid");
        console.log(userId)
        const response = await fetch(`http://127.0.0.1:8000/clock-records/${userId}`, requestOptions);
        const data = await response.json();
        
        console.log("API Response:", data);
        setAttendanceData(
          data && Array.isArray(data.clock_records)
            ? data.clock_records
            : []
        );
        setLoading(false);
        setError(null);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
        setError(error);
        setAttendanceData([]);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const currentDate = new Date();
    const currentMonth = currentDate.toLocaleString("default", {
      month: "long",
    });
    setSelectedMonth(currentMonth);
  }, []);

  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const years = ["2024"];

  const handleMonthChange = (month) => {
    setSelectedMonth(month);
  };

  const handleYearChange = (year) => {
    setSelectedYear(year);
  };

  const filteredAttendanceData = attendanceData.filter((row) => {
    const rowDate = new Date(row.date);
    const monthMatch =
      !selectedMonth || rowDate.getMonth() === months.indexOf(selectedMonth);
    const yearMatch =
      !selectedYear || rowDate.getFullYear() === parseInt(selectedYear);
    return monthMatch && yearMatch;
  });

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredAttendanceData.slice(
    indexOfFirstItem,
    indexOfLastItem
  );

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="rounded-md w-full px-[7rem] my-4">
      <div className="w-full h-full bg-whte shadow-lg rounded-md border border-gray-200">
        <header className="px-5 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="font-semibold text-gray-800">Timing</h2>
          <div>
            <select
              className="border rounded-md p-1 mr-2 text-sm font-semibold text-gray-800"
              onChange={(e) => handleMonthChange(e.target.value)}
            >
              <option className="font-semibold text-gray-800" value="">
                Months
              </option>
              {months.map((month, index) => (
                <option
                  className="text-sm font-semibold text-gray-600"
                  key={index}
                  value={month}
                >
                  {month}
                </option>
              ))}
            </select>
            <select
              className="border rounded-md p-1 text-sm font-semibold text-gray-800"
              onChange={(e) => handleYearChange(e.target.value)}
            >
              <option className="font-semibold text-gray-800" value="">
                Years
              </option>
              {years.map((year, index) => (
                <option
                  className="text-sm font-semibold text-gray-600"
                  key={index}
                  value={year}
                >
                  {year}
                </option>
              ))}
            </select>
          </div>
        </header>
        <div className="p-3">
          <div>
            <table className="table-auto w-full overflow-y-auto">
              <thead className="text-xs font-semibold uppercase text-black bg-[#6d9eeb7a]">
                <tr>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Date</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Login Time</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Logout Time</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">
                      Total hours of working
                    </div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Status</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-center">Remark</div>
                  </th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-gray-100">
                {currentItems.map((row, index) => (
                  <tr key={index}>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">{row.date}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">{row.clockin}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">{row.clockout}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">
                        {row.total_hours_worked}
                      </div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">{row.status}</div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-center">{row.remark}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div className="mt-2 flex justify-between items-center">
        <div>
          <button
            className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white mr-2"
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <button
            className="py-1 px-3 bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white"
            onClick={() => paginate(currentPage + 1)}
            disabled={indexOfLastItem >= filteredAttendanceData.length}
          >
            Next
          </button>
        </div>
        <div className="text-sm font-semibold text-gray-800">
          Page {filteredAttendanceData.length > 0 ? currentPage : 0} of{" "}
          {filteredAttendanceData.length > 0
            ? Math.ceil(filteredAttendanceData.length / itemsPerPage)
            : 0}
        </div>
      </div>
    </div>
  );
}