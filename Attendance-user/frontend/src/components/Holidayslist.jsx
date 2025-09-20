import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Holidayslist = () => {
  const [showAllHolidays, setShowAllHolidays] = useState(false);

  const holidays = [
    { date: 'Monday, 15 Jan', name: 'Pongal' },
    { date: 'Tuesday, 16 Jan', name: 'Thiruvalluvar Day' },
    { date: 'Friday, 26 Jan', name: 'Republic Day (G)' },
    { date: 'Sunday, 14 Apr', name: 'Tamil New Year' },
    { date: 'Wednesday, 01 May', name: 'May Day (G)' },
    { date: 'Thursday, 15 Aug', name: 'Independence Day (G)' },
    { date: 'Saturday, 07 Sep', name: 'Vinayagar Chathurthi' },
    { date: 'Wednesday, 02 Oct', name: 'Gandhi Jayanthi (G)' },
    { date: 'Saturday, 12 Oct', name: 'Vijaya Dasami' },
    { date: 'Thursday, 31 Oct', name: 'Diwali' },
  ];

  const firstHalf = holidays.slice(0, 5);
  const secondHalf = holidays.slice(5);

  return (
    
      
      <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md">
      <h1 className="text-5xl font-semibold font-poppins pb-4 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
          Leave Management
        </h1>
        <div className="flex justify-between mt-3">
          <h3 className="text-2xl font-semibold font-poppins py-2 text-zinc-500">
            Holidays Calendar
          </h3>
          <Link to="/User/Leave">
            <div className="">
            <button className=" px-4 py-2 text-base bg-blue-500 rounded-md text-white hover:bg-[#b7c6df80] hover:text-black  active:bg-white active:text-white">
                Go Back
              </button>
            </div>
          </Link>
        </div>

        <div className="flex justify-between space-x-6">
          <div className="w-1/2 ">
           
            <div className="holiday-list-container" >
              {firstHalf.map((holiday, index) => (
                <p key={index} className="bg-gradient-to-r from-white to-blue-100 border-x rounded-lg shadow-md p-2 my-3 text-gray-800 font-poppins px-6">
                  <span className="text-sm font-normal mr-1">{holiday.date}</span> <span className="text-sm font-bold">{holiday.name}</span>
                </p>
              ))}
            </div>
          </div>

          <div className="w-1/2 ">
            
            <div className="holiday-list-container" >
              {secondHalf.map((holiday, index) => (
                <p key={index} className="bg-gradient-to-r from-white to-blue-100 border-x rounded-lg shadow-md p-2 my-3 text-gray-800 font-poppins px-6">
                  <span className="text-sm font-normal mr-1">{holiday.date}</span> <span className="text-sm font-bold">{holiday.name}</span>
                </p>
              ))}
            </div>
          </div>
        </div>

        <p className='text-sm font-poppins text-gray-800 italic pt-2'><span className='font-semibold'>Note: </span>(G) - Gazetted Holiday</p>
      </div>
    
  );
};

export default Holidayslist;
