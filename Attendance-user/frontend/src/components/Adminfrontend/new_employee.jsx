import React, { useState } from "react";
import { toast, ToastContainer } from "react-toastify"; // Import toast components
import "react-toastify/dist/ReactToastify.css"; // Import toast styles

const AddUser = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    address: "",
    position: "",
    department: "",
    dateOfJoining: "",
    education: [
      { degree: "", institution: "", year: "" }, // Initialize education as an array of objects
    ],
    skills: [{ name: "", level: "" }], // Initialize skills as an array of objects
  });

  const handleChange = (e, index, type) => {
    const { name, value } = e.target;

    if (type === "education") {
      const updatedEducation = [...formData.education];
      updatedEducation[index][name] = value;
      setFormData({ ...formData, education: updatedEducation });
    } else if (type === "skills") {
      const updatedSkills = [...formData.skills];
      updatedSkills[index][name] = value;
      setFormData({ ...formData, skills: updatedSkills });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const addEducation = () => {
    setFormData({
      ...formData,
      education: [...formData.education, { degree: "", institution: "", year: "" }],
    });
  };

  const addSkill = () => {
    setFormData({
      ...formData,
      skills: [...formData.skills, { name: "", level: "" }],
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Create the payload for the API
    const payload = {
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      position: formData.position,
      department: formData.department,
      address: formData.address,
      date_of_joining: formData.dateOfJoining,
      education: formData.education, // Keep education as an array of objects
      skills: formData.skills.map((skill) => ({
        name: skill.name,
        level: parseInt(skill.level) || 0, // Convert level to integer or default to 0
      })),
    };

    // Remove skills with empty name or level
    payload.skills = payload.skills.filter((skill) => skill.name && skill.level);

    try {
      const response = await fetch("http://127.0.0.1:8000/add_employee", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message || "Employee added successfully!"); // Show success message
        // Reset the form
        setFormData({
          name: "",
          email: "",
          phone: "",
          address: "",
          position: "",
          department: "",
          dateOfJoining: "",
          education: [{ degree: "", institution: "", year: "" }],
          skills: [{ name: "", level: "" }],
        });
      } else {
        toast.error(data.detail || "Error occurred while adding employee."); // Show error message
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("An error occurred while adding the employee."); // Show generic error message
    }
    console.log("Payload:", payload);
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <ToastContainer /> {/* Add ToastContainer for toast messages */}
      <form
        className="bg-white p-6 rounded-lg shadow-md w-full max-w-6xl border"
        onSubmit={handleSubmit}
      >
        <h2 className="text-xl font-semibold mb-6 text-center">Add New Employee</h2>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block mb-1">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block mb-1">Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block mb-1">Position</label>
            <input
              type="text"
              name="position"
              value={formData.position}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block mb-1">Department</label>
            <input
              type="text"
              name="department"
              value={formData.department}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block mb-1">Date of Joining</label>
            <input
              type="date"
              name="dateOfJoining"
              value={formData.dateOfJoining}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
          </div>

          <div className="col-span-4">
            <label className="block mb-1">Education</label>
            {formData.education.map((edu, index) => (
              <div key={index} className="grid grid-cols-3 gap-4 mb-2">
                <input
                  type="text"
                  name="degree"
                  placeholder="Degree"
                  value={edu.degree}
                  onChange={(e) => handleChange(e, index, "education")}
                  className="border border-gray-300 rounded px-3 py-2"
                  required
                />
                <input
                  type="text"
                  name="institution"
                  placeholder="Institution"
                  value={edu.institution}
                  onChange={(e) => handleChange(e, index, "education")}
                  className="border border-gray-300 rounded px-3 py-2"
                  required
                />
                <input
                  type="text"
                  name="year"
                  placeholder="Year"
                  value={edu.year}
                  onChange={(e) => handleChange(e, index, "education")}
                  className="border border-gray-300 rounded px-3 py-2"
                  required
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
            {formData.skills.map((skill, index) => (
              <div key={index} className="grid grid-cols-2 gap-4 mb-2">
                <input
                  type="text"
                  name="name"
                  placeholder="Skill Name"
                  value={skill.name}
                  onChange={(e) => handleChange(e, index, "skills")}
                  className="border border-gray-300 rounded px-3 py-2"
                  required
                />
                <input
                  type="number"
                  name="level"
                  placeholder="Skill Level"
                  value={skill.level}
                  onChange={(e) => handleChange(e, index, "skills")}
                  className="border border-gray-300 rounded px-3 py-2"
                  required
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
              value={formData.address}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              rows="2"
              required
            ></textarea>
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 rounded mt-6 hover:bg-blue-600 transition"
        >
          Add
        </button>
      </form>
    </div>
  );
};

export default AddUser;
