import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useParams } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";

const EmployeeDetails = () => {
    const [error, setError] = useState(null);
    const [employeeData, setEmployeeData] = useState({
        userid: '',
        name: '',
        email: '',
        personal_email: '',
        resume_link: '',
        TL: '',
        phone: '',
        address: '',
        position: '',
        department: '',
        date_of_joining: '', // Changed from dateOfJoining to match backend
        education: [
            { degree: '', institution: '', year: '' },
        ],
        skills: [{ name: '', level: '' }],
        status: '', // Added missing status field
    });
    const [options, setOptions] = useState([]);
    const { id } = useParams();

    const ip = import.meta.env.VITE_HOST_IP;

    useEffect(() => {
        const fetchdata = async () => {
            try {
                const response = await axios.get(`${ip}/get_user/${id}`);
                const EmployeeDtls = response.data;

                const safeEmployeeData = {
                    userid: EmployeeDtls.userid || id, // Use userid from response, not _id
                    name: EmployeeDtls.name || '',
                    email: EmployeeDtls.email || '',
                    personal_email: EmployeeDtls.personal_email || '',
                    resume_link: EmployeeDtls.resume_link || '',
                    TL: EmployeeDtls.TL || '',
                    phone: EmployeeDtls.phone || '',
                    address: EmployeeDtls.address || '',
                    position: EmployeeDtls.position || '',
                    department: EmployeeDtls.department || '',
                    date_of_joining: EmployeeDtls.date_of_joining || '', // Match backend field name
                    education: EmployeeDtls.education || [{ degree: '', institution: '', year: '' }],
                    skills: EmployeeDtls.skills || [{ name: '', level: '' }],
                    status: EmployeeDtls.status || '', // Added status field
                };
                setEmployeeData(safeEmployeeData);
            } catch (error) {
                console.error("Error fetching employee data:", error);
                setEmployeeData({
                    userid: '',
                    name: '',
                    email: '',
                    personal_email: '',
                    resume_link: '',
                    TL: '',
                    phone: '',
                    address: '',
                    position: '',
                    department: '',
                    date_of_joining: '',
                    education: [{ degree: '', institution: '', year: '' }],
                    skills: [{ name: '', level: '' }],
                    status: '',
                });
            }
        };

        fetchdata();
    }, [id, ip]);

    useEffect(() => {
        fetch(`${ip}/get_managers_list`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setOptions(data);
            })
            .catch(error => {
                setError(error);
            });
    }, [ip]);

    // Fixed addEducation function
    const addEducation = () => {
        setEmployeeData({
            ...employeeData,
            education: [...employeeData.education, { degree: "", institution: "", year: "" }],
        });
    };

    // Fixed addSkill function
    const addSkill = () => {
        setEmployeeData({
            ...employeeData,
            skills: [...employeeData.skills, { name: "", level: "" }],
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Get client IP (you'll need to implement this or pass it from somewhere)
        const clientIP = "127.0.0.1"; // Replace with actual IP detection

        const payload = {
            userid: employeeData.userid,
            name: employeeData.name,
            email: employeeData.email,
            personal_email: employeeData.personal_email,
            resume_link: employeeData.resume_link,
            TL: employeeData.TL,
            phone: employeeData.phone,
            position: employeeData.position,
            department: employeeData.department,
            address: employeeData.address,
            date_of_joining: employeeData.date_of_joining, // Fixed field name
            education: employeeData.education.filter(edu =>
                edu.degree || edu.institution || edu.year
            ), // Filter out empty education entries
            skills: employeeData.skills
                .filter(skill => skill.name && skill.level) // Filter out empty skills
                .map((skill) => ({
                    name: skill.name,
                    level: parseInt(skill.level) || 0,
                })),
            status: employeeData.status, // Added status field
            ip: clientIP, // Added required IP field
        };

        console.log("Payload:", payload);

        try {
            const response = await fetch(`${ip}/edit_employee`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                toast.success(data.message || "Employee Updated successfully!");
            } else {
                toast.error(data.detail || "Error occurred while updating employee.");
            }
        } catch (error) {
            console.error("Error:", error);
            toast.error("An error occurred while updating the employee.");
        }
    };

    // Individual change handlers
    const handleNameChange = (e) => {
        setEmployeeData({ ...employeeData, name: e.target.value });
    };

    const handleEmailChange = (e) => {
        setEmployeeData({ ...employeeData, email: e.target.value });
    };

    const handlePemailChange = (e) => {
        setEmployeeData({ ...employeeData, personal_email: e.target.value });
    };

    const handlePhoneChange = (e) => {
        setEmployeeData({ ...employeeData, phone: e.target.value });
    };

    const handlePositionChange = (e) => {
        setEmployeeData({ ...employeeData, position: e.target.value });
    };

    const handleDepartmentChange = (e) => {
        setEmployeeData({ ...employeeData, department: e.target.value });
    };

    const handleDateofjoinChange = (e) => {
        setEmployeeData({ ...employeeData, date_of_joining: e.target.value });
    };

    const handleTLChange = (e) => {
        setEmployeeData({ ...employeeData, TL: e.target.value });
    };

    const handleStatusChange = (e) => {
        setEmployeeData({ ...employeeData, status: e.target.value });
    };

    const handleEducationChange = (e, index) => {
        const { name, value } = e.target;
        const updatedEducation = [...employeeData.education];
        updatedEducation[index][name] = value;
        setEmployeeData({ ...employeeData, education: updatedEducation });
    };

    const handleSkillChange = (e, index) => {
        const { name, value } = e.target;
        const updatedSkills = [...employeeData.skills];
        updatedSkills[index][name] = value;
        setEmployeeData({ ...employeeData, skills: updatedSkills });
    };

    const handleAddressChange = (e) => {
        setEmployeeData({ ...employeeData, address: e.target.value });
    };

    const handleResumeChange = (e) => {
        setEmployeeData({ ...employeeData, resume_link: e.target.value });
    };

    return (
        <div className="min-h-screen flex items-center justify-center">
            <form
                className="bg-white p-6 rounded-lg shadow-md w-full max-w-6xl border"
                onSubmit={handleSubmit}
            >
                <h2 className="text-xl font-semibold mb-6 text-center">Employee Details</h2>
                <div className="grid grid-cols-4 gap-4">
                   
                    <div>
                        <label className="block mb-1">Name</label>
                        <input
                            type="text"
                            name="name"
                            value={employeeData.name}
                            onChange={handleNameChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={employeeData.email}
                            onChange={handleEmailChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Personal Email</label>
                        <input
                            type="email"
                            name="personal_email"
                            value={employeeData.personal_email}
                            onChange={handlePemailChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Phone</label>
                        <input
                            type="tel"
                            name="phone"
                            value={employeeData.phone}
                            onChange={handlePhoneChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Position</label>
                        <input
                            type="text"
                            name="position"
                            value={employeeData.position}
                            onChange={handlePositionChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Department</label>
                        <input
                            type="text"
                            name="department"
                            value={employeeData.department}
                            onChange={handleDepartmentChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Date of Joining</label>
                        <input
                            type="date"
                            name="date_of_joining"
                            value={employeeData.date_of_joining}
                            onChange={handleDateofjoinChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block mb-1">Select TL</label>
                        <select
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            value={employeeData.TL}
                            onChange={handleTLChange}
                        >
                            <option value="">--select--</option>
                            {options.map((item, index) => (
                                <option key={index} value={item.name}>{item.name}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block mb-1">Status</label>
                        <select
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            value={employeeData.status}
                            onChange={handleStatusChange}
                        >
                            <option value="">--select--</option>
                            <option value="Active">Active</option>
                            <option value="Inactive">Inactive</option>
                            <option value="On Leave">On Leave</option>
                        </select>
                    </div>

                    <div className="col-span-4">
                        <label className="block mb-1">Education</label>
                        {employeeData.education.map((edu, index) => (
                            <div key={`education-${index}`} className="grid grid-cols-3 gap-4 mb-2">
                                <input
                                    type="text"
                                    name="degree"
                                    placeholder="Degree"
                                    value={edu.degree}
                                    onChange={(e) => handleEducationChange(e, index)}
                                    className="border border-gray-300 rounded px-3 py-2"
                                />
                                <input
                                    type="text"
                                    name="institution"
                                    placeholder="Institution"
                                    value={edu.institution}
                                    onChange={(e) => handleEducationChange(e, index)}
                                    className="border border-gray-300 rounded px-3 py-2"
                                />
                                <input
                                    type="text"
                                    name="year"
                                    placeholder="Year"
                                    value={edu.year}
                                    onChange={(e) => handleEducationChange(e, index)}
                                    className="border border-gray-300 rounded px-3 py-2"
                                />
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={addEducation}
                            className="text-blue-500 mt-2"
                        >
                            Add Another Education
                        </button>
                    </div>

                    <div className="col-span-4">
                        <label className="block mb-1">Skills</label>
                        {employeeData.skills.map((skill, index) => (
                            <div key={`skill-${index}`} className="grid grid-cols-2 gap-4 mb-2">
                                <input
                                    type="text"
                                    name="name"
                                    placeholder="Skill Name"
                                    value={skill.name}
                                    onChange={(e) => handleSkillChange(e, index)}
                                    className="border border-gray-300 rounded px-3 py-2"
                                />
                                <input
                                    type="number"
                                    name="level"
                                    placeholder="Skill Level"
                                    value={skill.level}
                                    onChange={(e) => handleSkillChange(e, index)}
                                    className="border border-gray-300 rounded px-3 py-2"
                                />
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={addSkill}
                            className="text-blue-500 mt-2"
                        >
                            Add Another Skill
                        </button>
                    </div>

                    <div className="col-span-4">
                        <label className="block mb-1">Address</label>
                        <textarea
                            name="address"
                            value={employeeData.address}
                            onChange={handleAddressChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            rows="2"
                            required
                        />
                    </div>

                    <div className="col-span-4">
                        <label className="block mb-1">Resume Link</label>
                        <input
                            type="text"
                            name="resume_link"
                            value={employeeData.resume_link}
                            onChange={handleResumeChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="w-full bg-blue-500 text-white py-2 rounded mt-6 hover:bg-blue-600 transition"
                >
                    Update Employee
                </button>
            </form>
            <ToastContainer />
            
        </div>
    );
};

export default EmployeeDetails;



// import React ,{useState,useEffect} from "react";
// import axios from "axios";
// import Datetime from "react-datetime";
// import { Link,useParams } from "react-router-dom";
// import { LS,ipadr } from "../Utils/Resuse";
// import { toast, ToastContainer } from "react-toastify";



// const EmployeeDetails =()=>{
//     const [error, setError] = useState(null);
//       const [employeeData, setEmployeeData] = useState({
//         userid:'',
//         name: '',
//         email: '',
//         personal_email:'',
//         resume_link:'',
//         TL:'',
//         phone: '',
//         address: '',
//         position: '',
//         department: '',
//         dateOfJoining: '',
//         education: [
//           { degree: '', institution: '', year: '' }, // Initialize education as an array of objects
//         ],
//         skills: [{ name: '', level: '' }], // Initialize skills as an array of objects
//       });
//       const [options, setOptions] = useState([]);
//       const {id}=useParams();

//       console.log("id is",{id});

//       useEffect(()=>{
//         const fetchdata=async ()=>{
//           try{
//             const response= await axios.get(`${ipadr}/get_user/${id}`);
//             const EmployeeDtls=response.data;
//             // console.log("employee dtls:",EmployeeDtls);

//             const empArray=Object.entries(EmployeeDtls);

//             const safeDetails = Array.isArray(empArray) ? empArray : [];
//               safeDetails.map((item ,index)=> {
//               // console.log("Details",item +"-"+ index)
//          },[]);

//          const safeEmployeeData = {
//           userid:EmployeeDtls._id|| id,
//           name: EmployeeDtls.name || '',
//           email: EmployeeDtls.email || '',
//           personal_email: EmployeeDtls.personal_email || '',
//           resume_link: EmployeeDtls.resume_link || '',
//           TL: EmployeeDtls.TL || '',
//           phone: EmployeeDtls.phone || '',
//           address: EmployeeDtls.address || '',
//           position: EmployeeDtls.position || '',
//           department: EmployeeDtls.department || '',
//           dateOfJoining: EmployeeDtls.date_of_joining || '',
//           education: EmployeeDtls.education || [{ degree: '', institution: '', year: '' }],
//           skills: EmployeeDtls.skills || [{ name: '', level: '' }],
//         };
//          setEmployeeData(safeEmployeeData);
            
//           }
//           catch(error)
//           {
//             setEmployeeData({
//               userid:'',
//               name: '',
//               email: '',
//               personal_email: '',
//               resume_link: '',
//               TL: '',
//               phone: '',
//               address: '',
//               position: '',
//               department: '',
//               dateOfJoining: '',
//               education: [{ degree: '', institution: '', year: '' }],
//               skills: [{ name: '', level: '' }],
//             });
//           }
        
//         };
//         fetchdata();
//       },[id])

//       useEffect(() => {
//           fetch(`${ipadr}/get_managers_list`) 
//             .then(response => {
//               if (!response.ok) {
//                 throw new Error('Network response was not ok');
//               }
//               return response.json();
//             })
//             .then(data => {
//               setOptions(data); // Store the fetched data in state
              
//             })
//             .catch(error => {
//               setError(error); // Handle any errors
             
//             });
//         }, []);

       

//       // console.log(employeeData);

//       // const empArray=Object.values(employeeData);
      

//       // const safeDetails = Array.isArray(empArray) ? empArray : [];
//       // //  safeDetails.map(item => {
//       // //         console.log("Details",item)
//       // //    });

//       //    console.log("details",safeDetails);

     
//       console.log("Employee data",employeeData);

//       const formattedDate = new Date(employeeData.dateOfJoining).toLocaleDateString('en-GB', {
//    day: '2-digit',
//    month: '2-digit',
//    year: 'numeric',
//  });



//  const formatDate = (dateString) => {
//   const date = new Date(dateString);
//   return date.toLocaleDateString("en-GB");
// };


// // console.log(formatDate(employeeData.dateOfJoining)); // Output: "03-02-2024"


// // const date=new Date(employeeData.dateOfJoining);
// // console.log(date);

// // const year = date.getFullYear();
// //       const month = String(date.getMonth() + 1).padStart(2, "0");
// //       const day = String(date.getDate()).padStart(2, "0");
// //       const formattedDate = `${year}-${month}-${day}`;

// //  console.log("date:",formattedDate);
      
//       const handleSelectChange =(event)=>{
//         setSelectedValue(event.target.value);
//       };

//       const handleChange = (e, index, type) => {
//         const { name, value } = e.target;}
    
//         const addEducation = () => {
//           // setFormData({
//           //   ...employeeData,
//           //   education: [...employeeData.education, { degree: "", institution: "", year: "" }],
//           // });
//           setEmployeeData((prev) => ({
// ...prev,
// education: [...(prev.education || []), { degree: "", institution: "", year: "" }],
// }));
//         };
      
//         const addSkill = () => {
//           // setFormData({
//           //   ...employeeData,
//           //   skills: [...employeeData.skills, { name: "", level: "" }],
//          setEmployeeData((prev) => ({
// ...prev,
// skills: [...(prev.skills || []), { name: "", level: "" }],
// }));
        
//         };

     


//       const handleSubmit=async(e)=>{
        

//         e.preventDefault();
        
           
//             // const payload = {
//             //   userid:employeeData.userid,
//             //   name: employeeData.name,
//             //   email: employeeData.email,
//             //   personal_email:employeeData.personal_email,
//             //   resume_link:employeeData.resume_link,
//             //   TL:employeeData.TL,
//             //   phone: employeeData.phone,
//             //   position: employeeData.position,
//             //   department: employeeData.department,
//             //   address: employeeData.address,
//             //   date_of_joining: employeeData.dateOfJoining||"",
//             //   education: employeeData.education, // Keep education as an array of objects
//             //   skills: employeeData.skills.map((skill) => ({
//             //     name: skill.name,
//             //     level: parseInt(skill.level) || 0, // Convert level to integer or default to 0
//             //   })),
//             // };

//             const payload = {
//   userid: employeeData.userid,
//   name: employeeData.name,
//   email: employeeData.email,
//   personal_email: employeeData.personal_email || "",
//   resume_link: employeeData.resume_link || "",
//   TL: employeeData.TL || "",
//   phone: employeeData.phone,
//   position: employeeData.position,
//   department: employeeData.department,
//   address: employeeData.address,
// // date_of_joining: employeeData.dateOfJoining || "",
// date_of_joining: employeeData.dateOfJoining || null,
//   education: employeeData.education || [],
//   skills: (employeeData.skills || [])
//     .filter((s) => s.name && s.level)
//     .map((s) => ({ name: s.name, level: parseInt(s.level, 10) })),
// };


          
        
//             // Remove skills with empty name or level
//             payload.skills = payload.skills.filter((skill) => skill.name && skill.level);
//             // setEmployeeData(payload);
//             console.log("Payload:", payload);
        
//             try {
//               const response = await fetch(`${ipadr}/edit_employee`, {
//                 method: "PUT",
//                 headers: {
//                   "Content-Type": "application/json",
//                 },
//                 // body: JSON.stringify(employeeData),
//                  body: JSON.stringify(payload), 
//               });
        
//               const data = await response.json();
        
//               if (response.ok) {
//                 toast.success(data.message || "Employee Updated successfully!"); // Show success message
               
//               } else {
//                 toast.error(data.detail || "Error occurred while adding employee."); // Show error message
//               }
//             } catch (error) {
//               console.error("Error:", error);
//               toast.error("An error occurred while adding the employee."); // Show generic error message
//             }
            

//       }

//       const handleNameChange=(e)=>{
//         setEmployeeData({...employeeData,name:e.target.value});
//       }

//       const handleEmailChange=(e)=>{
//         setEmployeeData({...employeeData,email:e.target.value});
//       }

//       const handlePemailChange=(e)=>{
//         setEmployeeData({...employeeData,personal_email:e.target.value});
//       }

//       const handlePhoneChange=(e)=>{
//         console.log("value:",e.target.value);
//         setEmployeeData({...employeeData,phone:e.target.value});
//       }

//       const handlePositionChange=(e)=>{
//         setEmployeeData({...employeeData,position:e.target.value});
//       }

//       const handleDepartmentChange=(e)=>{
//         setEmployeeData({...employeeData,department:e.target.value});
//       }

//       const handleDateofjoinChange=(e)=>{
//         setEmployeeData({...employeeData,dateOfJoining:e.target.value});
//       }

//       const handleTLChange=(e)=>{
//         setEmployeeData({...employeeData,TL:e.target.value});
//       }

//       const handleEducationChange=(e,index)=>{
//         const { name, value } = e.target;
//         const updatedSkills = [...employeeData.education];
//         updatedSkills[index][name] = value;
//         setEmployeeData({...employeeData,education:updatedSkills});
//       }

//       // const handleSkillChange=(e)=>{
//       //   setEmployeeData({...employeeData,skills:e.target.value});
//       // }

//       const handleSkillChange = (e,index) => {
        
//         const { name, value } = e.target;
//         console.log(index,name);
//         // console.log(index,field,value);
//         // const updatedSkills = skills.map((skill, i) =>
//         //   i === index ? { ...skill, [field]: value } : skill
//         // );
//         // setEmployeeData(updatedSkills);
//         const updatedSkills = [...employeeData.skills];
//         updatedSkills[index][name] = value;
//         setEmployeeData({ ...employeeData, skills: updatedSkills });
//       };


//       // const handleSkillChange = (e, index) => {
//       //    const { name, value } = e.target.value;

//       //   const updatedSkills = [...employeeData.skills];
//       //   updatedSkills[index][name] = value;
//       //   setEmployeeData({ ...employeeData, skills: updatedSkills });
//       // };
      
      
      

//       const handleAddressChange=(e)=>{
//         setEmployeeData({...employeeData,address:e.target.value});
//       }

//       const handleResumeChange=(e)=>{
//         setEmployeeData({...employeeData,resume_link:e.target.value});
//       }


//       return(
//         <div className="min-h-screen flex items-center justify-center">
          
//           <form
//         className="bg-white p-6 rounded-lg shadow-md w-full max-w-6xl border"
//         onSubmit={(e)=>handleSubmit(e)}>
//         <h2 className="text-xl font-semibold mb-6 text-center">Employee Details</h2>
//         <div className="grid grid-cols-4 gap-4">
          
//              <div>
//              <label className="block mb-1">Name</label>
//              <input
//                type="text"
//                name="name"
//                value={employeeData.name}
//                onChange={handleNameChange}
//                className="w-full border border-gray-300 rounded px-3 py-2"
//                required
               
//              />
//            </div>
//            <div>
//            <label className="block mb-1">email</label>
//              <input
//                type="email"
//                name="email"
//                value={employeeData.email}
//                onChange={handleEmailChange}
//                className="w-full border border-gray-300 rounded px-3 py-2"
//                required
//              />
//            </div>
//            <div>
//           <label className="block mb-1">Personal Email</label>
//           <input
//               type="email"
//               name="personal_email"
//               value={employeeData.personal_email}
//               onChange={handlePemailChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               // required
//             />
//           </div>
//           <div >
//             <label className="block mb-1">Phone</label>
//             <input
//               type="tel"
//               name="phone"
//               value={employeeData.phone}
//               onChange={handlePhoneChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               required
//             />
//           </div>
//           <div >
//             <label className="block mb-1">Position</label>
//             <input
//               type="text"
//               name="position"
//               value={employeeData.position}
//               onChange={handlePositionChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               required
//             />
//           </div>
//           <div>
//             <label className="block mb-1">Department</label>
//             <input
//               type="text"
//               name="department"
//               value={employeeData.department}
//               onChange={handleDepartmentChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               required
//             />
//           </div>
//           <div>
//             <label className="block mb-1">Date of Joining</label>
//             <input
//               type="text"
//               name="dateOfJoining"
//               value={employeeData.dateOfJoining||""}
//               onChange={handleDateofjoinChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               required
//               // disabled
//             />
//           </div>
//           <div >
//           <label className="block mb-1"> Select TL</label>
//           <select  className="w-full border border-gray-300 rounded px-3 py-2" value={employeeData.TL} onChange={handleTLChange}>
//             <option>--select--</option>
//             {
//               options.map((item,index)=>(
//                 <option key={index} value={item.name}>{item.name}</option>
//               ))
//             }
//           </select>
//           </div>

//           <div  className="col-span-4">
//             <label className="block mb-1">Education</label>
//             {
//               employeeData.education.map((edu,index)=>(
//                 <div key={`education-${index}`}  className="grid grid-cols-3 gap-4 mb-2">
//                 <input
//                   type="text"
//                   name="degree"
//                   placeholder="Degree"
//                   value={edu.degree}
//                   onChange={(e) => handleEducationChange(e, index)}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//                 <input
//                   type="text"
//                   name="institution"
//                   placeholder="Institution"
//                   value={edu.institution}
//                   onChange={(e) => handleEducationChange(e, index)}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//                 <input
//                   type="text"
//                   name="year"
//                   placeholder="Year"
//                   value={edu.year}
//                   onChange={(e) => handleEducationChange(e, index)}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//               </div>
                
//               ))
//             }
//             {/* { 
//               <div  className="grid grid-cols-3 gap-4 mb-2">
//                 <input
//                   type="text"
//                   name="degree"
//                   placeholder="Degree"
//                   value={employeeData.education?.[0]?.degree}
//                   onChange={(e) => handleEducationChange(e, index, "education")}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//                 <input
//                   type="text"
//                   name="institution"
//                   placeholder="Institution"
//                   value={employeeData.education?.[0]?.institution}
//                   onChange={(e) => handleEducationChange(e, index, "education")}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//                 <input
//                   type="text"
//                   name="year"
//                   placeholder="Year"
//                   value={employeeData.education?.[0]?.year}
//                   onChange={(e) => handleEducationChange(e, index, "education")}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//               </div>
//             } */}
//             <button
//               type="button"
//               onClick={addEducation}
//               className="text-blue-500 mt-2"
//             >
//               Add Another Education
//             </button>
//           </div>

//           <div  className="col-span-4">
//             <label className="block mb-1">Skills</label>
//             {
//               employeeData.skills.map((skill,index)=>(
//                 <div key={`skill-${index}`} className="grid grid-cols-2 gap-4 mb-2"  >
//                 <input
//                   type="text"
//                   name="name"
//                   placeholder="Skill Name"
//                   value={skill.name}
//                   onChange={(e) => handleSkillChange(e,index)}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//                 <input
//                   type="number"
//                   name="level"
//                   placeholder="Skill Level"
//                   value={skill.level}
//                   onChange={(e) => handleSkillChange( e,index)}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//               </div>
//               ))
             
//            }
//             <button
//               type="button"
//               onClick={addSkill}
//               className="text-blue-500 mt-2"
//             >
//               Add Another Skill
//             </button>
//           </div>

//           <div  className="col-span-4">
//             <label className="block mb-1">Address</label>
//             <textarea
//               name="address"
//               value={employeeData.address}
//               onChange={handleAddressChange}
//               className="w-full border border-gray-300 rounded px-3 py-2"
//               rows="2"
//               required
//             ></textarea>
//           </div>
//           <div  className="col-span-4">
//              <label className="block mb-1">Resume Link</label>
//              <input
//                   type="text"
//                   name="resume_link"
//                   value={employeeData.resume_link}
//                   onChange={ handleResumeChange}
//                   className="border border-gray-300 rounded px-3 py-2"
//                   // required
//                 />
//           </div>

//         </div>
//         <button
//           type="submit"
//           className="w-full bg-blue-500 text-white py-2 rounded mt-6 hover:bg-blue-600 transition"
//         >
//           Confirm
//         </button>
//       </form>
//         </div>
//       )
// };

// export default EmployeeDetails;