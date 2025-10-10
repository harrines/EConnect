// src/components/HRDocsReview.jsx
import { useState, useEffect } from "react";
import {
  Check,
  FileText,
  X,
  User,
  PlusCircle,
  Upload,
  CheckCircle,
  Clock,
  Trash2,
  Eye,
} from "lucide-react";
import axios from "axios";
import { ipadr } from "../../Utils/Resuse";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function HRDocsReview() {
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [newDocName, setNewDocName] = useState("");
  const [assignedDocs, setAssignedDocs] = useState({});
  const [reviewUser, setReviewUser] = useState(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingAssign, setLoadingAssign] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoadingUsers(true);
      const res = await axios.get(`${ipadr}/get_all_users`);
      const normalizedUsers = res.data.map((u) => ({
        ...u,
        userId: u.id || u._id || u.userId,
      }));
      setUsers(normalizedUsers);
      await Promise.all(normalizedUsers.map((user) => fetchAssignedDocs(user.userId)));
    } catch (err) {
      console.error(" Error fetching users:", err);
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchAssignedDocs = async (userId) => {
    try {
      const res = await axios.get(`${ipadr}/documents/assigned/${userId}`);
      setAssignedDocs((prev) => ({ ...prev, [userId]: res.data }));
    } catch (err) {
      console.error(` Error fetching docs for user ${userId}:`, err);
    }
  };

  const toggleUserSelection = (userId) => {
    setSelectedUsers((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  const handleAssignDocument = async () => {
    if (!selectedUsers.length) return alert("Select at least 1 user.");
    if (!newDocName.trim()) return alert("Enter a document name.");
    const docNameTrimmed = newDocName.trim();

    try {
      setLoadingAssign(true);
      setAssignedDocs((prev) => {
        const updated = { ...prev };
        selectedUsers.forEach((uid) => {
          const prevDocs = prev[uid] || [];
          updated[uid] = [
            ...prevDocs,
            { docName: docNameTrimmed, status: "pending", assignedBy: "HR", fileUrl: null },
          ];
        });
        return updated;
      });

      await axios.post(`${ipadr}/assign_docs`, {
        userIds: selectedUsers,
        docName: docNameTrimmed,
      });

      await Promise.all(selectedUsers.map((uid) => fetchAssignedDocs(uid)));
      setNewDocName("");
      setSelectedUsers([]);
    } catch (err) {
      console.error(err);
      alert(" Failed to assign document");
    } finally {
      setLoadingAssign(false);
    }
  };

  const handleVerify = async (userId, docName) => {
    try {
      await axios.put(`${ipadr}/review_document`, {
        userId,
        docName,
        status: "verified",
        remarks: "Verified by HR",
      });
      fetchAssignedDocs(userId);
    } catch (err) {
      console.error(err);
      alert(" Verification failed");
    }
  };

 const handleDelete = (userId, docName) => {
  toast(
    ({ closeToast }) => (
      <div className="flex flex-col gap-2">
        <span>Are you sure you want to delete <strong>{docName}</strong>?</span>
        <div className="flex justify-end gap-2">
          <button
            onClick={async () => {
              closeToast(); // close the confirmation toast
              try {
                await axios.delete(`${ipadr}/assigned_doc_delete`, {
                  data: { userId, docName },
                });
                setAssignedDocs((prev) => ({
                  ...prev,
                  [userId]: (prev[userId] || []).filter((d) => d.docName !== docName),
                }));
                toast.success("Document deleted successfully!");
              } catch (err) {
                console.error(err);
                toast.error("Failed to delete document");
              }
            }}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs"
          >
            Yes
          </button>
          <button
            onClick={closeToast}
            className="px-3 py-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 text-xs"
          >
            No
          </button>
        </div>
      </div>
    ),
    {
      autoClose: false,
      closeOnClick: false,
      draggable: false,
    }
  );
};


  <ToastContainer position="top-center" />


  const filteredUsers = users.filter((user) =>
    user.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filterDocsByStatus = (docs) => {
    if (statusFilter === "all") return docs;
    return docs.filter((doc) => {
      if (statusFilter === "pending") return !doc.fileUrl;
      if (statusFilter === "uploaded") return doc.fileUrl && doc.status !== "verified";
      if (statusFilter === "verified") return doc.status === "verified";
      return true;
    });
  };

  return (
    <div className="mr-8 p-10 bg-gray-50 min-h-[90vh] w-full rounded-xl justify-center items-center ml-10">
      <h1 className="text-4xl font-bold text-gray-800 border-b pb-2 mb-6">
        Admin Documents Review
      </h1>

      {selectedUsers.length > 0 && (
        <div className="mb-6 flex gap-5 items-center bg-white shadow p-4 rounded-lg">
          <input
            type="text"
            placeholder="Enter Document Name"
            value={newDocName}
            onChange={(e) => setNewDocName(e.target.value)}
            className="px-3 py-2 border rounded-lg w-72 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <button
            onClick={handleAssignDocument}
            disabled={loadingAssign}
            className="px-4 py-2 bg-blue-400 text-white rounded-lg flex items-center gap-2 hover:bg-blue-500 disabled:opacity-50"
          >
            <PlusCircle size={18} /> {loadingAssign ? "Assigning..." : "Assign"}
          </button>
        </div>
      )}

      <div className="mb-4 flex flex-col md:flex-row gap-3 items-center">
        <input
          type="text"
          placeholder="Search users by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-72 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-48 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="uploaded">Uploaded</option>
          <option value="verified">Verified</option>
        </select>
      </div>

      {loadingUsers ? (
        <p className="text-center text-gray-600">Loading users...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredUsers.map((user) => {
            const userDocs = filterDocsByStatus(assignedDocs[user.userId] || []);
            return (
              <div
                key={user.userId}
                className="bg-white rounded-lg shadow-sm p-4 flex flex-col justify-between hover:shadow-md transition"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                    {user.name?.[0]?.toUpperCase() || <User size={20} />}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-800">{user.name}</div>
                    <div className="text-sm text-gray-500">{userDocs.length} Documents</div>
                  </div>
                </div>

                <div className="mt-4 flex justify-between items-center">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      className="form-checkbox text-blue-600 rounded"
                      checked={selectedUsers.includes(user.userId)}
                      onChange={() => toggleUserSelection(user.userId)}
                    />
                    Select
                  </label>
                  <button
                    onClick={() => setReviewUser(user)}
                    className="px-3 py-1 bg-blue-300 text-white rounded-lg hover:bg-blue-400 text-sm"
                  >
                    Review
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {reviewUser && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white rounded-xl shadow-lg w-11/12 md:w-2/3 lg:w-1/2 p-6 max-h-[80vh] overflow-y-auto relative">
            <button
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
              onClick={() => setReviewUser(null)}
            >
              <X size={20} />
            </button>
            <h2 className="text-xl font-bold mb-4 text-gray-800">
              {reviewUser.name} - Assigned Documents
            </h2>

            <table className="w-full text-left border-collapse">
              <thead className="bg-gray-100 sticky top-0 z-10">
                <tr>
                  <th className="py-2 px-6">Document</th>
                  <th className="py-2 px-6">Status</th>
                  <th className="py-2 px-6">Assigned By</th>
                  <th className="py-2 px-6">Action</th>
                </tr>
              </thead>
              <tbody>
                {filterDocsByStatus(assignedDocs[reviewUser.userId] || []).map((doc) => (
                  <tr key={doc.docName} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-4 flex items-center gap-2 text-gray-800">
                      <FileText size={16} className="text-blue-500" />
                      {doc.docName}
                    </td>
                    <td className="py-2 px-2">
                      {doc.status === "verified" ? (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                          <CheckCircle size={12} /> Verified
                        </span>
                      ) : doc.fileUrl ? (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                          <Upload size={12} /> Uploaded
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                          <Clock size={12} /> Pending
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-4 text-gray-700">{doc.assignedBy || "-"}</td>
                    <td className="py-2 px-4 flex gap-2">
                      {doc.fileUrl && (
                        <a
                          href={`${ipadr}${doc.fileUrl}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-600 text-sm underline flex items-center gap-1"
                        >
                          <Eye size={14} />
                        </a>
                      )}
                      {doc.fileUrl && doc.status !== "verified" && (
                        <button
                          onClick={() => handleVerify(reviewUser.userId, doc.docName)}
                          className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 flex items-center gap-1 text-xs"
                        >
                          <Check size={14} />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(reviewUser.userId, doc.docName)}
                        className="px-2 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 flex items-center gap-1 text-xs"
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
