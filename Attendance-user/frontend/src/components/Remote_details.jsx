import { Link } from "react-router-dom";
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Baseaxios, LS } from "../Utils/Resuse";

const Remote_details = () => {
  const [RemoteWorkData, setRemoteWorkData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userid = LS.get("userid");
        const RemoteWorkResponse = await axios.get(
          `http://127.0.0.1:8000/Remote-History/${userid}`
        );
        console.log("API Response:", RemoteWorkResponse.data);
        setRemoteWorkData(
          RemoteWorkResponse.data &&
            Array.isArray(RemoteWorkResponse.data.Remote_History)
            ? RemoteWorkResponse.data.Remote_History
            : []
        );
        setLoading(false);
        setError(null);
      } catch (error) {
        console.error("Error fetching data:", error);
        setLoading(false);
        setRemoteWorkData([]);
        setError("Error fetching data. Please try again later.");
      }
    };

    fetchData();
  }, []);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = RemoteWorkData.slice(indexOfFirstItem, indexOfLastItem);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md">
      <h1 className="text-5xl font-semibold font-poppins pb-4 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text">
        Remotework Management
      </h1>
      <div className="flex justify-end mb-4">
        {/* <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
          Remotework Details
        </h3> */}
        <Link to="/User/LeaveHistory">
          <div className="">
            <button className=" mr-3 px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
              Go Back
            </button>
          </div>
        </Link>

        <Link to="/User/LeaveHistory">
          <div className="">
            <button className="px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
              Leave Details
            </button>
          </div>
        </Link>
      </div>
      <div className="my-2">
        <div className=" border p-4 rounded-lg shadow-xl">
          <h2 className="text-lg font-semibold mb-4 font-poppins">
            Remotework History
          </h2>
          {loading ? (
            <p>Loading...</p>
          ) : error ? (
            <p>{error}</p>
          ) : RemoteWorkData && RemoteWorkData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-500">
                <thead className="text-xs text-black uppercase bg-[#6d9eeb7a]">
                  <tr>
                    <th scope="col" className="p-2 font-poppins text-center">
                      Date
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      Employee ID
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      Employee Name
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      From Date
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      To Date
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      Reason
                    </th>
                    <th scope="col" className="p-2 font-poppins text-center">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="text-sm text-gray-700 bg-white">
                  {currentItems.map((RemoteWork, index) => (
                    <tr key={index}>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.requestDate}
                      </td>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.userid}
                      </td>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.employeeName}
                      </td>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.fromDate}
                      </td>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.toDate}
                      </td>
                      <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.reason}
                      </td>
                      {/* {RemoteWork.status?(
                        <td scope="col" className="p-2 font-poppins text-center">
                        {RemoteWork.status }
                      </td>
                      ):(
                        <td scope="col" className="p-2 font-poppins text-center">
                        Pending
                      </td>
                      )} */}

{RemoteWork.status ? (
  <td
    scope="col"
    className={`p-2 font-poppins text-center ${
      RemoteWork.status === "Approved"
        ? "text-green-500"
        : RemoteWork.status === "Rejected"
        ? "text-red-500"
        : ""
    }`}
  >
    {RemoteWork.status}
  </td>
) : (
  <td scope="col" className="p-2 font-poppins text-center">
    Pending
  </td>
)}

                      
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm italic font-poppins">No records found</p>
          )}
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
              disabled={indexOfLastItem >= RemoteWorkData.length}
            >
              Next
            </button>
          </div>
          <div className="text-sm font-semibold text-gray-800">
            {/* Page {currentPage} of {Math.ceil(filteredAttendanceData.length / itemsPerPage)} */}
            Page {RemoteWorkData.length > 0 ? currentPage : 0} of{" "}
            {RemoteWorkData.length > 0
              ? Math.ceil(RemoteWorkData.length / itemsPerPage)
              : 0}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Remote_details;
