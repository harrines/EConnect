import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch, faDownload } from "@fortawesome/free-solid-svg-icons";
import axios from "axios";

const Timemanagement = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const formattedDate = formatDate(selectedDate);
        const response = await axios.get(
          `http://127.0.0.1:8000/attendance/?date=${formattedDate}`
        );
        const filteredData =
          response.data && Array.isArray(response.data.attendance)
            ? response.data.attendance.filter((item) =>
              item.name.toLowerCase().includes(searchTerm.toLowerCase())
            )
            : [];
        setAttendanceData(filteredData);
        setLoading(false);
        setError(null);
      } catch (error) {
        setLoading(false);
        setAttendanceData([]);
        setError("Error fetching data");
      }
    };

    fetchData();
  }, [selectedDate, searchTerm]);

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const disableSunday = (date) => {
    return date.getDay() !== 0;
  };

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = attendanceData.slice(indexOfFirstItem, indexOfLastItem);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const downloadExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(attendanceData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "AttendanceData");
    XLSX.writeFile(workbook, "attendance_data.xlsx");
  };

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback  ml-10 rounded-md">
      <div className="">
        <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
          Clock In & Clock Out
        </h1>
        <div className="w-full bg-gradient-to-b from-white to-blue-50 shadow-lg rounded-xl border border-gray-200 my-2 mt-10">
          <header className="px-4 py-4 border-b border-gray-200 flex justify-between">
            <DatePicker
              selected={selectedDate}
              onChange={(date) => setSelectedDate(date)}
              dateFormat="dd-MM-yyyy"
              className="border border-gray-300 rounded-md w-24 px-2 py-1 text-sm text-center"
              style={{ backgroundColor: "#f7fafc", cursor: "pointer" }}
              placeholderText="Select date"
              minDate={new Date("01-01-2024")}
              maxDate={new Date("31-12-2024")}
              filterDate={disableSunday}
            />
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
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Name</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Clockin</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Clockout</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Hours of Working</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Status</div>
                    </th>
                    <th scope="col" className="p-2 whitespace-nowrap">
                      <div className="font-semibold text-center">Remark</div>
                    </th>
                  </tr>
                </thead>

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
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">
                            {index + 1 + (currentPage - 1) * itemsPerPage}.
                          </div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.name}</div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.clockin}</div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.clockout}</div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.total_hours_worked}</div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.status}</div>
                        </td>
                        <td scope="col" className="p-2 whitespace-nowrap">
                          <div className="font-medium text-center">{row.remark} </div>
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
              className="py-1 px-3 bg-blue-500 hover:bg-blue-400 text-white text-sm font-inter rounded-full shadow-lg mr-2"
              onClick={() => paginate(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <button
              className="py-1 px-3 bg-blue-500 hover:bg-blue-400 text-white text-sm font-inter rounded-full shadow-lg"
              onClick={() => paginate(currentPage + 1)}
              disabled={indexOfLastItem >= attendanceData.length}
            >
              Next
            </button>
          </div>
          <div className="text-sm font-semibold text-gray-800">
            Page {attendanceData.length > 0 ? currentPage : 0} of{" "}
            {attendanceData.length > 0
              ? Math.ceil(attendanceData.length / itemsPerPage)
              : 0}
          </div>
          <button
            className="py-1 px-3 bg-[#3B82F6] hover:bg-green-400 text-white text-sm font-inter rounded-full shadow-lg"
            onClick={downloadExcel}
          >
            <FontAwesomeIcon icon={faDownload} /> Download Excel
          </button>
        </div>
      </div>
    </div>
  );
};

export default Timemanagement;
