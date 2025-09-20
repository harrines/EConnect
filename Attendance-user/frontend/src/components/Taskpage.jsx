import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FaTrashAlt, FaEdit, FaCheckCircle, FaRegCircle } from "react-icons/fa";
import { LS,ipadr } from "../Utils/Resuse";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const TaskPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [date, setDate] = useState("");
  const userId = LS.get("userid"); // Replace with dynamic user ID
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [newTask, setNewTask] = useState("");
  const [duedate,setDuedate]=useState("");
  console.log(userId);
  // Check if the selected date is today or a future date
  const isPastDate = (selectedDate) => {
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0'); // Ensures two digits for day
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Get month (0-based index, so add 1)
    const year = today.getFullYear();
    
    const formattedDate = `${day}-${month}-${year}`;
    console.log(formattedDate);
    
    const selected = new Date(selectedDate);
    const selectedDay = String(selected.getDate()).padStart(2, '0'); // Renamed to avoid conflict
    const selectedMonth = String(selected.getMonth() + 1).padStart(2, '0');
    const selectedYear = selected.getFullYear();
    
    const formattedSelectedDate = `${selectedMonth}-${selectedDay}-${selectedYear}`;
    console.log(formattedSelectedDate);
    
    if (formattedSelectedDate < formattedDate) {
        return true;
      } else {
        return false;
      }
      
  };

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const dateFromQuery = queryParams.get("date");
    setDate(dateFromQuery || "");

    if (dateFromQuery) {
      fetchTasks(userId, dateFromQuery);
    }
  }, [location, userId]);

  const fetchTasks = async (userId, selectedDate) => {
    setLoading(true);
    setErrorMessage("");
    console.log(selectedDate);
    try {
      const response = await fetch(
        `${ipadr}/get_tasks/${userId}/${selectedDate}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to fetch tasks");
      }

      const data = await response.json();
      if (data.message) {
        setTasks([]); // No tasks found
      } else {
        setTasks(data);
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const addTask = async () => {
    if (newTask.trim() === "") {
      toast.error("Task cannot be empty.");
      return;
    }
    // console.log("task",newTask,userId,date);
   
    setErrorMessage("");
    try {
      console.log(newTask,userId,date,duedate)
      const response = await fetch(`${ipadr}/add_task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          task: newTask,
          userid: userId,
          date: date,
          due_date:duedate,
        }),
      });
     
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to add task");
      }

      toast.success("Task added successfully!");
      fetchTasks(userId, date);
      setNewTask("");
      setDuedate("");
    } catch (error) {
      toast.error(error.message);
    }
  };

  const editTask = async (index, updatedTask) => {
    const taskToEdit = tasks[index];

    console.log(taskToEdit);
    if (updatedTask.trim() === "" || updatedTask === taskToEdit.task) {
      toast.error("Task cannot be empty or unchanged.");
      return;
    }

    try {
      const response = await fetch(`${ipadr}/edit_task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userid: userId,
          task: taskToEdit.task,
          updated_task: updatedTask,
          status: taskToEdit.status,
          date: date,
          due_date:taskToEdit.due_date,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update task");
      }

      toast.success("Task updated successfully!");
      fetchTasks(userId, date);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const confirmDelete = (taskIndex) => {
    if (window.confirm("Are you sure you want to delete this task?")) {
      deleteTask(taskIndex);
    }
  };

  const deleteTask = async (taskIndex) => {
    const taskToDelete = tasks[taskIndex];
    console.log(taskToDelete);
    try {
      const response = await fetch(`${ipadr}/task_delete`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          task: taskToDelete.task,
          userid: userId,
          status:taskToDelete.status,
          date: date,
          due_date:taskToDelete.due_date,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to delete task");
      }

      toast.success("Task deleted successfully!");
      fetchTasks(userId, date);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const confirmToggleStatus = (taskIndex) => {
    console.log(taskIndex);
    const taskToUpdate = tasks[taskIndex];
    console.log(taskToUpdate);
    const newStatus = taskToUpdate.status === "Completed" ? "Pending" : "Completed";
    const message = newStatus === "Completed" ? 
      "Are you sure you want to mark this task as completed?" : 
      "Are you sure you want to mark this task as pending?";

    if (window.confirm(message)) {
      toggleTaskStatus(taskIndex);
    }
  };

  const toggleTaskStatus = async (taskIndex) => {
    const taskToUpdate = tasks[taskIndex];
    const newStatus = taskToUpdate.status === "Completed" ? "Pending" : "Completed";
console.log(newStatus,duedate);
    try {
      const response = await fetch(`${ipadr}/edit_task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userid: userId,
          task: taskToUpdate.task,
          updated_task: taskToUpdate.task,
          status: newStatus,
          date: date,
          due_date:taskToUpdate.due_date,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update task status");
      }

      toast.success(`Task marked as ${newStatus}!`);
      fetchTasks(userId, date);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const renderManagerTasks = () =>{

  }

  const renderTasks = () => {
    if (loading) {
      return <p className="text-gray-500">Loading tasks...</p>;
    }

    if (errorMessage) {
      return <p className="text-red-500">{errorMessage}</p>;
    }

    if (tasks.length === 0) {
      return <p className="text-gray-500">No tasks for this date.</p>;
    }

    return (
      <ul className="space-y-4">
        {tasks.map((task, index) => (
          <li
            key={index}
            className="flex justify-between items-center bg-white p-4 rounded-lg shadow-sm border border-gray-200 w-full"
          >
            <div className="flex items-center">
              <button
                onClick={() => confirmToggleStatus(index)}
                className={`mr-3 text-xl ${
                  task.status === "Completed" 
                    ? "text-green-500 hover:text-green-600" 
                    : "text-gray-400 hover:text-gray-500"
                } transition-colors`}
                aria-label={`Mark task as ${task.status === "Completed" ? "incomplete" : "complete"}`}
              >
                {task.status === "Completed" ? <FaCheckCircle /> : <FaRegCircle />}
              </button>
              <span className={`text-lg text-gray-800 ${task.status === "Completed" ? "" : ""}`}>
                {task.task} <br/> due date:{task.due_date}      
              </span> 
             
              {!isPastDate(date) && (
                <button
                  onClick={() => {
                    const newTaskText = prompt("Edit task:", task.task);
                    if (newTaskText !== null && newTaskText !== task.task) {
                      editTask(index, newTaskText);
                    }
                  }}
                  className="ml-4 text-yellow-500 hover:text-yellow-600 transition-colors"
                >
                  <FaEdit />
                </button>
              )}
            </div>
            {!isPastDate(date) && (
              <button
                onClick={() => confirmDelete(index)}
                className="text-red-500 hover:text-red-700 transition-colors"
              >
                <FaTrashAlt />
              </button>
            )}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-gray-100 w-full">
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      <div className="flex-1 p-8 bg-white w-full overflow-auto">
        <div className="flex justify-between items-center mb-6 pb-5 border-b-2">
          <h2 className="text-3xl font-semibold text-gray-800">
            Tasks on {date || "Date not available"}
          </h2>
          <button
            onClick={() => navigate("/User/todo")}
            className="p-3 bg-blue-600 text-white rounded-lg"
          >
            Back to Calendar
          </button>
        </div>

        {!isPastDate(date) && (
          <div className="mb-8">
            <div className="flex items-center justify-between space-x-8 mb-6">
              <input
                type="text"
                className="p-3 border border-gray-300 rounded-lg w-full lg:w-[700px] xl:w-[800px] 2xl:w-[900px]"
                placeholder="Enter new task"
                aria-label="Enter task"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addTask()}
              />
              <button
                onClick={addTask}
                className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add
              </button>
            </div>
            <div >
            Due date : 
              <input
              name="due date"
              type="date"
               className="p-3 border border-gray-300 rounded-lg w-full lg:w-[300px] xl:w-[300px] 2xl:w-[300px]"
               placeholder="Enter due date"
               aria-label="Enter date"
               value={duedate}
               onChange={(e) => setDuedate(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && addTask()}
              />
            </div>

            {errorMessage && <p className="text-red-500 text-sm">{errorMessage}</p>}
            <p className="text-sm text-gray-600">Press "Enter" to add a task</p>
          </div>
        )}

        <div className="bg-gray-50 p-6 rounded-lg shadow-sm w-full max-h-[400px] overflow-y-auto">
          {renderTasks()}
        </div>
         {/* Manager Task:
        <div className="bg-gray-50 p-6 rounded-lg shadow-sm w-full max-h-[400px] overflow-y-auto">
          {renderManagerTasks()}
        </div> */}
      </div>
    </div>
  );
};

export default TaskPage;