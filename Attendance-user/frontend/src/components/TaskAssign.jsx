import { AiFillCloseSquare } from 'react-icons/ai';

const Form=({ modeldata,toggleForm, setToggleForm, handleonSubmit, handleAllChange, note })=> {
  
// const handleAllChange=(e,index,type)=>{
//   const {name,value}=e.target;

// //    console.log(name +"-"+ value);

//   setModelData({ ...modeldata, [name]: value });
// }
  return (
    <div
      className={
        !toggleForm
          ? 'w-full h-screen mx-auto flex justify-center items-center absolute top-[-200%] left-0 right-0 bg-[#5756564f] z-10'
          : 'w-full h-screen mx-auto flex justify-center items-center absolute top-0 bg-[#5756564f] z-10'
      }
    >
      <form
        className="flex justify-start flex-col bg-gray-50 px-5 py-10 rounded-md relative"
        onSubmit={handleonSubmit}
      >
       <div>
             <label className="block mb-1">Task</label>
             <textarea
               name="task"
               value={modeldata.task}
               onChange={handleAllChange}
               className="w-full border border-gray-300 rounded px-3 py-2"
             ></textarea>
           </div>
           <div>
            <label className="block mb-1">Due date</label>
            <input 
               type="date"
                name="due_date"
                value={modeldata.due_date}
                onChange={handleAllChange}
                className="w-full border border-gray-300 rounded px-3 py-2"
                />
           </div>
        <button className="p-4 bg-blue-600 text-white mt-3 rounded" type="submit">
          Save
        </button>

        <div
          className="absolute top-2 right-5 text-xl font-bold text-red-400 cursor-pointer"
          onClick={() => setToggleForm(!toggleForm)}
        >
          <AiFillCloseSquare size={30} />
        </div>
      </form>
    </div>
  );
}


import { AiOutlineDelete, AiOutlineEdit } from 'react-icons/ai';

const Note = ({ empdata, handleDelete, handleEdit }) => {
  return (
    <div
    className={`${
      empdata.bg ? empdata.bg : 'bg-green-300'
    } p-6 pt-12 w-[320px] min-h-[250px] relative flex flex-col  
      rounded-lg shadow-xl border-l-[10px] border-grey-500 
      transition-all transform hover:scale-105 hover:-translate-y-2 
      hover:shadow-2xl hover:z-10 animate-fade-in`}
  >
    {/* Sticky Tape Effect */}
    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-6 bg-gray-400 opacity-30 rounded-b-lg"></div>
  
    {/* Task Details */}
    <p className="text-gray-900 font-bold text-xl mb-3 text-center">📝 Task Details</p>
    <ul className="text-gray-800 text-base space-y-2">
      <li><span className="font-semibold">Task:</span> {empdata.task}</li>
      <li><span className="font-semibold">Assigned Date:</span> {empdata.date}</li>
      <li><span className="font-semibold">Due Date:</span> {empdata.due_date}</li>
      <li>
        <span className="font-semibold">Status:</span> 
        <span className={`ml-2 px-3 py-1 text-xs font-bold roun</ul>ded-full shadow-md 
          ${empdata.status === 'Completed' ? 'bg-green-500 text-white' : 
          empdata.status === 'Pending' ? 'bg-yellow-500 text-black' : 
          'bg-red-500 text-white'}`}>
          {empdata.status}
        </span>
      </li>
    </ul>
  
    {/* Action Buttons with Floating Effect */}
    <div className="absolute top-2 right-4 flex gap-2">
      <button
        className="bg-green-600 text-white p-2 rounded-full shadow-lg transition-transform transform hover:scale-110 hover:shadow-green-500"
        onClick={() => handleEdit(empdata.taskid)}
      >
        <AiOutlineEdit className="text-xl" />
      </button>
      <button
        className="bg-red-600 text-white p-2 rounded-full shadow-lg transition-transform transform hover:scale-110 hover:shadow-red-500"
        onClick={() => handleDelete(empdata.taskid)}
      >
        <AiOutlineDelete className="text-xl" />
      </button>
    </div>
  </div>
  );
};









import React,{useState,useEffect} from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { ipadr,LS } from "../Utils/Resuse";
import { Modal } from "./Modal";
import { createPortal } from "react-dom";
import { FaEdit } from "react-icons/fa";
import { toast,ToastContainer } from "react-toastify";
import Multiselect from 'multiselect-react-dropdown';
import { FaCheck } from "react-icons/fa"; 
import { DateRangePicker } from "react-date-range";
import { format, isWithinInterval, parseISO } from 'date-fns';
import { useParams } from 'react-router-dom';
import { ArrowUp, ArrowDown, ArrowUpDown, RotateCw } from "lucide-react";

const TaskAssign=()=>{
     const [employeeData, setEmployeeData] = useState({});
     const [taskData,SetTaskData]=useState([]);
     const [loading, setLoading] = useState(false);
     const [error,setError]=useState();
     const [currentPage, setCurrentPage] = useState(1);
     const [itemsPerPage, setItemsPerPage] = useState(5);
    //  const [selectAll, setSelectAll] = useState(false);
    //  const [selectedUsers, setSelectedUsers] = useState([]);
    //  const [data,setData]=useState();
    const [openmodel,SetOpenmodel]=useState(false)
    const [modalOpen, setModalOpen] = useState(false);
    const [selectone,SetSelectone]=useState({});
    const [allselect,SetAllSelect]=useState({});
    const[tempdata,SetTempdata]=useState({});
    const [options, SetOptions] = useState([]);

     
      const [selectedValue, setSelectedValue] = useState('');
      const [ValueSelected, SetValueSelected] = useState("");
      const [selectedUsers, setSelectedUsers] = useState([]);


      const [showDatePicker, setShowDatePicker] = useState(false);
      const [dateRange, setDateRange] = useState([
          {
            startDate: null,
            endDate: null,
            key: "selection",
          },
        ]);
      const [filteredData, setFilteredData] = useState([]);
       const [sortConfig, setSortConfig] = useState({
          column: null,
          direction: 'asc'
        });


    const [editModel,SetEditmodel]=useState([]);

    const[modeldata,setModelData]=useState({
        task:[""],
          userid:"",
          date:"",
          due_date:"",
          TL:"",
        
    })
    const isManager=LS.get('position')==="Manager"? true:false;

    const user_id=useParams();
    const userid=LS.get('userid')

    console.log("userid:",userid);
    
    
     let url=''

     console.log("isManager:",isManager);

     if(isManager)
     {
      url=`${ipadr}/get_assigned_task?TL=${LS.get('name')}`
     }
     else{
      url=`${ipadr}/get_tasks/${userid}`
     }

     useEffect(()=>{
        fetchEmpdata();
        //confirm();
        users();
        //dropdown();

     },[])
     const fetchEmpdata= async()=>{
      try{
          setLoading(true);
          const response= await axios.get(`${url}`);
          const Empdata=response.data && Array.isArray(response.data)? response.data :[];
          console.log("data:",Empdata);
          setEmployeeData(Empdata);
          setFilteredData(Empdata);
          setLoading(false);
      }
      catch(error)
      {
          setLoading(false);
          setEmployeeData([]);
           setError("Error while fetching");
      }
  }

    //  const handleCheckboxChange = (id) => {
    //     setEmployeeData((prevData) =>
    //       prevData.map((item) =>
    //         item.id === id ? { ...item, checked: !item.checked } : item
    //       )
    //     );
    //   };
 

     


      const handleChange = (e) => {
        const {name , checked} = e.target ;

        console.log(name);

        if(name == "allSelect") {
            
            let tempEmp = employeeData.map(item => {
                return {...item,isChecked: checked,category:name}
            }) ;
            console.log(tempEmp);
            SetAllSelect(tempEmp);
            setEmployeeData(tempEmp) ;
        }
        else { 
            console.log("SelectOne")
            let tempUser = employeeData.map(item => item.name === name ? {...item, isChecked: checked,category: "SelectOne"} : item);
            console.log(tempUser);
            let user= Object.assign(tempUser.filter(item=>item.category==="SelectOne"));
            console.log(user)
            SetSelectone(user);
            setEmployeeData(tempUser) ;
        }
    }

    const handletaskeditChange=(e)=>{
      const { name, value } = e.target;
      console.log("name:",name,"- value:",value );

      SetEditmodel((prevData) => ({
          ...prevData,
          Task_details: prevData.Task_details.map((item, index) =>
              index === 0 ? { ...item, [name]: value } : item
          )
        
      }));
    }

    // 🔥 Fix in handleduedateeditChange
    const handleduedateeditChange = (e) => {
        const { value } = e.target;   // ✅ fixed
        console.log(value);
        SetEditmodel({
            ...editModel,
            due_date: value
        });
    };


    const handleEditmodel = (index, e) => {
      const { name, value } = e.target;
      const updatedEditModel = [...editModel]; // Clone the array
      updatedEditModel[index] = { ...updatedEditModel[index], [name]: value }; // Update specific object
      SetEditmodel(updatedEditModel);
    };
    
    const handleAllChange=(e,index,type)=>{
       const {name,value}=e.target;

       console.log(name +"-"+ value);

       setModelData({ ...modeldata, [name]: value });
    }

    const handleforAllChange = (e) => {
      const { name, value } = e.target;
      console.log("name:",name,"- value:",value );

      setModelData((prevData) => ({
          ...prevData,
          Task_details: prevData.Task_details.map((item, index) =>
              index === 0 ? { ...item, [name]: value } : item
          )
        
      }));
      
  };
  console.log("duedate:",modeldata.due_date);
    

    const handleButtonClick = (value) => {
        setModalOpen(false);
        SetOpenmodel(false);
        
      };

      const handleTaskChange = (index, event) => {
        const newTasks = [...modeldata.task];
        newTasks[index] = event.target.value; 
        setModelData({ ...modeldata, task: newTasks, });
      };

      const today = new Date();
      const month = ("0" + (today.getMonth() + 1)).slice(-2);
      const year = today.getFullYear();
      const date = ("0" + today.getDate()).slice(-2);
      const currentDate = `${year}-${month}-${date}`;
      
      console.log(currentDate);
      

      const handleonSubmit=async(e)=>{
        
        // console.log("Data:",employeeData);
        let taskArr=[];
        // const response="";
       
        if(isManager){
          for(let i=0;i<selectedUsers.length;i++)
            {
              const taskdetails={
                
                
                  Tasks:modeldata.task,
                  userid:selectedUsers?.[i]?.userid,
                  TL:LS.get("name"),
                  date: currentDate,
                  due_date:modeldata.due_date,
                 
              };
                  taskArr.push(taskdetails);
            }
            // console.log(taskArr);
            
    
            console.log("taskArr:",taskArr);
            
               
                const response=  await axios({
                  method: 'post',
                  url: `${ipadr}/task_assign_to_multiple_members`,
                  data: {Task_details:taskArr}, 
                  headers: {
                   // 'Authorization': `bearer ${token}`,
                  'Content-Type': 'application/json'
                  }, 
                })
                if(response.status===200)
                  {
                     toast.success("Task Added successfully");
                     setModelData({
                        task:[""],
                        userid:"",
                        date:"",
                        due_date:"",
                        TL:"",
                    
                        
                     })
                  }
                  else{
                    toast.error("error while Added the data");
                  }
              setModalOpen(false);
               
        }
        else
        {
          const singletask={
            task:modeldata.task,
            userid:LS.get('userid'),
            date: currentDate,
            due_date:modeldata.due_date
          };
          console.log("singletask:",singletask);
          // response=  await axios({
          //   method: 'post',
          //   url: `${ipadr}/add_task`,
          //   data: {singletask}, 
          //   headers: {
          //    // 'Authorization': `bearer ${token}`,
          //   'Content-Type': 'application/json'
          //   }, 
          // })
           const response = await fetch(`${ipadr}/add_task`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    task: modeldata.task,
                    userid: LS.get('userid'),
                    date: currentDate,
                    due_date:modeldata.due_date,
                  }),
                });
                if(response.status===200)
                  {
                     toast.success("Task Added successfully");
                     setModelData({
                        task:[""],
                        userid:"",
                        date:"",
                        due_date:"",
                        // TL:"",
                    
                        
                     })
                  }
                  else{
                    toast.error("error while Added the data");
                  }
              setModalOpen(false);
        }
       
        
               
              
    
        fetchEmpdata();          

      }

       
       const deleteTask = async (taskIndex) => {
          const taskToDelete = employeeData[taskIndex];
          console.log("taskToDelete:",taskToDelete);
          try {
            const response = await fetch(`${ipadr}/task_delete/${taskIndex}`, {
              method: "DELETE",
              headers: {
                "Content-Type": "application/json",
              },
              // body: JSON.stringify({
              //   task: taskToDelete.task,
              //   userid: LS.get('userid'),
              //   status:taskToDelete.status,
              //   date: taskToDelete.date,
              //   due_date:taskToDelete.due_date,
              // }),
            });
      
            const data = await response.json();
            if (!response.ok) {
              throw new Error(data.detail || "Failed to delete task");
            }
      
            toast.success("Task deleted successfully!");
            fetchTasks(LS.get('id'), date);
          } catch (error) {
            toast.error(error.message);
          }
          fetchEmpdata();
        };

        const fetchTasks = async (userId, selectedDate) => {
            setLoading(true);
            // setErrorMessage("");
            console.log(selectedDate);
            try {
              const response = await fetch(
                `${ipadr}/get_tasks/${userid}/${selectedDate}`
              );
        
              if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch tasks");
              }
        
              const data = await response.json();
              if (data.message) {
                setEmployeeData([]); // No tasks found
              } else {
                setEmployeeData(data);
              }
            } catch (error) {
              setErrorMessage(error.message);
            } finally {
              setLoading(false);
            }
          };


      const handleoneditSubmit=async()=>{
        
          console.log("editmodel:",editModel);
          console.log("editmodel:",editModel?.[0]?.task);
         const updatedetails={
          updated_task:editModel?.[0]?.task,
          userid:editModel?.[0]?.userid,
          status:editModel?.[0]?.status,
          due_date:editModel?.[0]?.due_date,
          taskid:editModel?.[0]?._id
         }
         console.log("updateddetails:",updatedetails);


      const response=await  axios({
          method: 'put',
          url: `${ipadr}/edit_task`,
          data: updatedetails, 
          headers: {
            // 'Authorization': `bearer ${token}`,
           'Content-Type': 'application/json'
           },    
         });

         if(response.status===200)
         {
          toast.success("Task edited successfully");
         }
         else{
          toast.error("error while editing the data");
         }
         SetOpenmodel(false);
         fetchEmpdata();
      }



      // ✅ confirm function (handle single object too)
    // confirm function
      const confirm = async (id) => {
        if (!id) {
          console.error("No ID provided for confirm function");
          return;
        }

        try {
          const response = await axios.get(`${ipadr}/get_single_task/${id}`);
          let taskdetails = response.data;

          if (!Array.isArray(taskdetails)) {
            taskdetails = [taskdetails];
          }

          console.log("taskdetails:", taskdetails);
          SetEditmodel(taskdetails);
          SetOpenmodel(true);
        } catch (error) {
          console.error("Error in confirm function:", error);
          toast.error("Error fetching task details");
        }
      };

      let url1='';
      let url2='';
      
      if(isManager)
      {
        url1=`${ipadr}/get_team_members?TL=${LS.get('name')}`;
        url2=`${ipadr}/get_assigned_task?TL=${LS.get('name')}&userid=${ValueSelected}`
      }

      const users=async()=>{
        if (!isManager) return; // Only fetch users for managers
        
        try {
            const response = await axios.get(`${url1}`)
            const userdetails=response.data && Array.isArray(response.data) ? response.data:[];
            console.log("userdetails",userdetails)
            
            const hardcodedOption = {
                userid: LS.get("userid"),
                name: LS.get("name"),
                address:LS.get("address"),
                date_of_joining:LS.get("date_of_joining"),
                email:LS.get("email"),
                education:LS.get("education"),
                department:LS.get("department"),
                personal_email:LS.get("personal_email"),
                phone:LS.get("phone"),
                position:LS.get("position"),
                resume_link:LS.get("resume_link"),
                skills:LS.get("skills"),
                TL:LS.get("TL"),
                status:LS.get("status")
            };
        const updateddetails=[...userdetails,hardcodedOption];
        console.log("updateddetails",updateddetails);
        SetOptions(userdetails);
        } catch (error) {
            console.error("Error fetching users:", error);
            SetOptions([]);
        }
      }

      console.log("options:",options);
      
      const dropdown=async ()=>{
        if (!isManager || !ValueSelected) return;
        
        try {
            const response= await Baseaxios.get(`${url2}`);
            const Empdata=response.data && Array.isArray(response.data)? response.data :[];
            console.log("dropdowndata:",Empdata);
            setFilteredData(Empdata);
        } catch (error) {
            console.error("Error in dropdown:", error);
            setFilteredData([]);
        }
    }

      
      const [note, setNote] = useState({
        body: '',
        bg: ''
      });
      const [editNote, setEditNote] = useState();
      const [toggleForm, setToggleForm] = useState(false);
      const [toggleEditForm, setToggleEditForm] = useState(false);
    
      const handlesChange = (e) => {
        if (toggleEditForm) {
          setEditNote({ ...editNote, [e.target.name]: e.target.value });
        }
    
        if (toggleForm) {
          setNote({ ...note, [e.target.name]: e.target.value });
        }
      };
    

    
      const handleDelete = (id) => {
        const leftNotes = employeeData.filter((note) => note.id !== id);
        setEmployeeData(leftNotes);
      };
    
 
      const handleEditSubmit = (e) => {
        e.preventDefault();
    
        const updatedNotes = employeeData.map((note) => (note.id === editNote.id ? editNote : note));
    
        setEmployeeData(updatedNotes);
    
        setEditNote({});
        setToggleEditForm(!toggleEditForm);
      };
 
      const handleSelectChange =(event)=>{
        setSelectedValue(event.target.value);
      };
      
      const handleSelectvalueChange =(event)=>{
        SetValueSelected(event.target.value);
        dropdown();
      };

      useEffect(() => {
        dropdown();
      }, []);

      const addTask = () => {
        setModelData({ ...modeldata, task: [...modeldata.task, ""] });
      };
    
      const onSelect=(selectedList)=>{
        setSelectedUsers(selectedList);
        console.log("selected",selectedList);
      
      }
     const onRemove=(selectedList)=>{
      setSelectedUsers(selectedList);
      console.log("unselected:",selectedList);

     }

     const handleDateRangeChange = (ranges) => {
      const { startDate, endDate } = ranges.selection;
      setDateRange([ranges.selection]);
      filterDataByDateRange(startDate, endDate);
    };

    const filterDataByDateRange = (startDate, endDate) => {
            if (!startDate || !endDate) {
              setFilteredData(employeeData);
              return;
            }
        
            const filtered = employeeData.filter(item => {
              const itemDate = parseISO(convertDateFormat(item.date || item.due_date));
              return isWithinInterval(itemDate, {
                start: startDate,
                end: endDate
              });
            });
        
            const sortedData = sortConfig.column 
              ? sortData(filtered, sortConfig.column) 
              : filtered;
            
            setFilteredData(sortedData);
            setCurrentPage(1);
          };

          const convertDateFormat = (dateString) => {
            if (!dateString) return '';
            const [day, month, year] = dateString.split('-');
            return `${year}-${month}-${day}`;
          };
          

          console.log("filter data:",filteredData);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredData.slice();

  console.log("currentItems:",currentItems)
          

  const handleReset = () => {
    setDateRange([{
      startDate: null,
      endDate: null,
      key: "selection"
    }]);
    setFilteredData(employeeData);
    // setCurrentPage(1);
    // setSortConfig({ column: null, direction: 'asc' });
    setShowDatePicker(false);
  };

     return(
        <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full  shadow-black rounded-xl justify-center items-center relative jsonback  ml-10 rounded-md h-screen overflow-y-scroll scrollbar-hide  ">
            <div className="">
            <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">
              Task Assign  </h1>
              <div className="">
              
             
       <header className="px-5 py-4 border-b border-gray-200 flex justify-between items-center">
            {/* <h2 className="font-semibold text-gray-800">Task Assign</h2> */}
            <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg" onClick={() => setModalOpen(true)}>
                    Add Task
             </button>


             
         <div className="flex items-center space-x-3"> 
          <div className="relative">
          {
            isManager ?(
              <>
              <select
                  className="w-48 border border-gray-400 rounded-lg px-4 py-2 text-gray-700 bg-white shadow-md outline-none focus:ring-2 focus:ring-blue-500 transition max-w-[200px] max-h-[40px]"
                  value={ValueSelected || ""}   // ✅ safe default
                  onChange={handleSelectvalueChange}
              >
                  <option value="">--select--</option>
                  {options.map(item => (
                      <option key={item.id || item.userid} value={item.userid}>
                          {item.name}
                      </option>
                  ))}
              </select>


          {/* <select  onClick={()=>dropdown()} className="w-48 border border-gray-400 rounded-lg px-4 py-2 text-gray-700 bg-white shadow-md outline-none focus:ring-2 focus:ring-blue-500 transition max-w-[100px] max-h-[40px]" value={ValueSelected} onChange={handleSelectvalueChange} >
            <option >--select--</option>
            {
              options.map(item=>(
                <option key={item.id} value={item.userid}>{item.name}</option>
              ))
            }
        </select> */}
        {/* <button className="bg-white-500 hover:bg-blue-400 hover:text-slate-900 text-black text-sm font-inter px-4 py-2 rounded-full shadow-lg absolute "  >
                      <FaCheck/>
        </button>  */}
              </>
            ):[]
          }
          {/* <select  className="w-48 border border-gray-400 rounded-lg px-4 py-2 text-gray-700 bg-white shadow-md outline-none focus:ring-2 focus:ring-blue-500 transition max-w-[100px] max-h-[40px]" value={ValueSelected} onChange={handleSelectvalueChange} >
                <option>--select--</option>
                <option key={LS.get('id')} value={LS.get('userid')} >{LS.get('name')}</option>
            {
              options.map(item=>(
                <option key={item.id} value={item.userid}>{item.name}</option>
              ))
            }
        </select>
        <button className="bg-white-500 hover:bg-blue-400 hover:text-slate-900 text-black text-sm font-inter px-4 py-2 rounded-full shadow-lg absolute " onClick={()=>dropdown()} >
                      <FaCheck/>
        </button>  */}
      </div>
     </div>
      
      


             <div className="flex items-center gap-4">
             <button
                onClick={handleReset}
                className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 flex items-center gap-2"
              >
                <RotateCw className="w-4 h-4" />
                Reset
              </button>
              
                  <div className="relative">
                    <button
                      onClick={() => setShowDatePicker(!showDatePicker)}
                      className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                    >
                      {showDatePicker ? 'Hide Date Range' : 'Show Date Range'}
                    </button>
                    {showDatePicker && (
                      <div className="absolute right-0 top-12 z-50 bg-white shadow-lg rounded-md border">
                        <DateRangePicker
                          ranges={dateRange}
                          onChange={handleDateRangeChange}
                          moveRangeOnFirstSelection={false}
                        />
                      </div>
                    )}
                  </div>
                 
                </div>
          </header>
                          

     
     
                 {/* <div className="w-full max-w-[200px] border border-gray-300 rounded px-3 py-2 " >
                 <Multiselect
                    options={options} // Options to display in the dropdown
                    selectedValues={selectedValue} // Preselected value to persist in dropdown
                    onSelect={onSelect} // Function will trigger on select event
                     onRemove={onRemove} // Function will trigger on remove event
                     displayValue="name" // Property name to display in the dropdown options
                     />
                 </div> */}
                    
     
 {/* <Link to={`/User/viewtask`}>
                <div className="">
                   <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg absolute top-[95px] right-[10px] ">
                      View Tasks
                    </button>                                                           
                 </div>
              </Link>  */}

              

      <div className="notes border-t-2 border-gray-200 mt-5 pt-5 container mx-auto grid md:grid-cols-4 gap-10 ">
        {currentItems.length > 0 ? (
          currentItems.map((item, i) => {
            return (
              <Note handleDelete={deleteTask} handleEdit={confirm} key={i} empdata={item} />
            );
          })
        ) : (
          <p> No notes. Please add one </p>
        )}
      </div>  


             {modalOpen &&
        createPortal(
          <Modal
            closeModal={handleButtonClick}
            onSubmit={handleonSubmit}
            onCancel={handleButtonClick}
          >
           
           <>
           <div className="max-h-[50vh] overflow-y-auto"> {/* Added scroll functionality */}
           {modeldata.task.map((task, index) => (
        <div key={index} className="mb-4">
          <label className="block text-lg font-semibold text-gray-700 mb-2">Task {index + 1}</label>
          <textarea
            name={`task-${index}`}
            value={task}
            onChange={(e) => handleTaskChange(index, e)}
            className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition placeholder-gray-500"
          ></textarea>
        </div>
          ))}
           <button
              type="button"
              onClick={addTask}
              className="bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium px-4 py-2 rounded-lg shadow-md hover:scale-105 transition transform"
            >
             ➕ Add Another Task
            </button>
            {
             
            <div className="mt-4">
            <label className="block text-lg font-semibold text-gray-700 mb-2">Due date</label>
            <input
               type="date"
                name="due_date"
                value={modeldata.due_date}
                onChange={handleAllChange}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:ring-2 focus:ring-pink-400 focus:border-pink-400 transition cursor-pointer"
                />
           </div>
             
            }
           {
            isManager? (
      <div className="mt-4">
       <label className="block text-lg font-semibold text-gray-700 mb-2">
    👤 Select User
       </label>
        <div className="w-full max-w-sm bg-white border border-gray-300 rounded-lg px-4 py-2 shadow-sm">
         <Multiselect
           options={options} // Options to display in the dropdown 
           selectedValues={selectedValue} // Preselected value to persist in dropdown
           onSelect={onSelect} // Function will trigger on select event
           onRemove={onRemove} // Function will trigger on remove event
           displayValue="name" // Property name to display in the dropdown options
           className="text-gray-700"
           />
           </div>
         </div>
            ):[]

           }
              </div>
            </>
          </Modal>,
          document.body
        )}

        {
         openmodel &&
         createPortal(
          <Modal
          closeModal={handleButtonClick}
            onSubmit={handleoneditSubmit}
            onCancel={handleButtonClick}>
              {
                editModel.map((item, index) => (
                  <div key={index}>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block mb-1">Task</label>
                        <textarea 
                          name="task"
                          value={item.task}
                          onChange={(e) => handleEditmodel(index, e)}
                          className="w-full border border-gray-300 rounded px-3 py-2"
                        ></textarea>
                      </div>
                      <div>
                        <label className="block mb-1">Due date</label>
                        <input 
                          type="text"
                          name="due_date"
                          value={item.due_date}
                          onChange={(e) => handleEditmodel(index, e)}
                          className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block mb-1">Status</label>
                      <input 
                        type="text"
                        name="status"
                        value={item.status}
                        onChange={(e) => handleEditmodel(index, e)}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                  </div>
                ))
                
                 
                
              }
         
          
              
            

          </Modal>,
          document.body
         )
        }

          </div>
        
            </div>

        </div>
     )
}

export default TaskAssign;