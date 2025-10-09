// src/components/HRDocsReview.jsx
import { useState, useEffect } from "react";
import { Check, FileText, X, User, PlusCircle, Upload, CheckCircle, Clock, Trash2, Eye } from "lucide-react";
import axios from "axios";
import { ipadr } from "../../Utils/Resuse";

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

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      setLoadingUsers(true);
      const res = await axios.get(`${ipadr}/get_all_users`);
      const normalizedUsers = res.data.map((u) => ({ ...u, userId: u.id || u._id || u.userId }));
      setUsers(normalizedUsers);
      await Promise.all(normalizedUsers.map((user) => fetchAssignedDocs(user.userId)));
    } catch (err) { console.error(err); } 
    finally { setLoadingUsers(false); }
  };

  const fetchAssignedDocs = async (userId) => {
    try {
      const res = await axios.get(`${ipadr}/documents/assigned/${userId}`);
      setAssignedDocs((prev) => ({ ...prev, [userId]: res.data }));
    } catch (err) { console.error(err); }
  };

  const toggleUserSelection = (userId) => {
    setSelectedUsers((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  const handleAssignDocument = async () => {
    if (!selectedUsers.length || !newDocName.trim()) return alert("Select users and enter document name");
    const docNameTrimmed = newDocName.trim();
    try {
      setLoadingAssign(true);
      setAssignedDocs((prev) => {
        const updated = { ...prev };
        selectedUsers.forEach((uid) => {
          updated[uid] = [...(prev[uid] || []), { docName: docNameTrimmed, status: "pending", assignedBy: "HR", fileUrl: null }];
        });
        return updated;
      });
      await axios.post(`${ipadr}/assign_docs`, { userIds: selectedUsers, docName: docNameTrimmed });
      await Promise.all(selectedUsers.map((uid) => fetchAssignedDocs(uid)));
      setNewDocName(""); setSelectedUsers([]);
    } catch (err) { console.error(err); alert("Failed to assign document"); } 
    finally { setLoadingAssign(false); }
  };

  const handleVerify = async (userId, docName) => {
    try { 
      await axios.put(`${ipadr}/review_document`, { userId, docName, status: "verified", remarks: "Verified by HR" });
      fetchAssignedDocs(userId);
    } catch { alert("Verification failed"); }
  };

  const handleDelete = async (userId, docName) => {
    try {
      if (!window.confirm(`Delete "${docName}"?`)) return;
      await axios.delete(`${ipadr}/assigned_doc_delete`, { data: { userId, docName } });
      setAssignedDocs((prev) => ({ ...prev, [userId]: (prev[userId] || []).filter(d => d.docName !== docName) }));
    } catch { alert("Failed to delete document"); }
  };

  const filteredUsers = users.filter(user => user.name?.toLowerCase().includes(searchTerm.toLowerCase()));
  const filterDocsByStatus = (docs) => {
    if (statusFilter === "all") return docs;
    return docs.filter(doc => statusFilter === "pending" ? !doc.fileUrl : statusFilter === "uploaded" ? doc.fileUrl && doc.status !== "verified" : doc.status === "verified");
  };

  return (
    <div className="p-10 bg-gray-50 min-h-screen rounded-xl">
      <h1 className="text-4xl font-bold text-blue-600 mb-8 border-b-2 border-blue-200 pb-3">HR Documents Review</h1>

      {/* Assign Section */}
      {selectedUsers.length > 0 && (
        <div className="flex flex-col md:flex-row gap-4 items-center bg-white p-4 rounded-lg shadow-md mb-6">
          <input
            type="text"
            placeholder="Enter Document Name"
            value={newDocName}
            onChange={(e) => setNewDocName(e.target.value)}
            className="px-3 py-2 border rounded-lg w-full md:w-72 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <button
            onClick={handleAssignDocument}
            disabled={loadingAssign}
            className="flex items-center gap-2 px-4 py-2 bg-green-400 text-white rounded-lg shadow hover:bg-green-500 disabled:opacity-50"
          >
            <PlusCircle size={18} /> {loadingAssign ? "Assigning..." : "Assign"}
          </button>
        </div>
      )}

      {/* Search & Filter */}
      <div className="flex flex-col md:flex-row gap-4 mb-6 items-center">
        <input
          type="text"
          placeholder="Search users by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-72 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg w-full md:w-48 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="uploaded">Uploaded</option>
          <option value="verified">Verified</option>
        </select>
      </div>

      {/* Users Grid */}
      {loadingUsers ? (
        <p className="text-center text-gray-500">Loading users...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredUsers.map(user => {
            const userDocs = filterDocsByStatus(assignedDocs[user.userId] || []);
            return (
              <div key={user.userId} className="bg-white rounded-2xl shadow-md p-4 flex flex-col justify-between hover:shadow-xl transition-all max-h-60 overflow-y-auto">
                {/* Header */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-lg">
                    {user.name?.[0]?.toUpperCase() || <User size={20} />}
                  </div>
                  <div>
                    <div className="font-semibold text-lg">{user.name}</div>
                    <div className="text-sm text-gray-500">{userDocs.length} Documents</div>
                  </div>
                </div>
                {/* Footer */}
                <div className="mt-auto flex justify-between items-center">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      className="form-checkbox text-blue-500 rounded"
                      checked={selectedUsers.includes(user.userId)}
                      onChange={() => toggleUserSelection(user.userId)}
                    />
                    Select
                  </label>
                  <button
                    onClick={() => setReviewUser(user)}
                    className="px-3 py-1 bg-blue-400 text-white rounded-lg hover:bg-blue-500 text-sm"
                  >
                    Review
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Review Modal */}
      {reviewUser && (
        <div className="fixed inset-0 bg-white/80 flex justify-center items-start pt-20 z-50 overflow-auto">
          <div className="bg-white rounded-2xl shadow-xl w-11/12 md:w-3/4 lg:w-1/2 p-6 max-h-[80vh] overflow-y-auto relative">
            <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700" onClick={() => setReviewUser(null)}>
              <X size={20} />
            </button>
            <h2 className="text-2xl font-bold mb-4">{reviewUser.name} - Assigned Documents</h2>
            <table className="w-full border-collapse">
              <thead className="bg-blue-50 sticky top-0 z-10">
                <tr>
                  <th className="py-2 px-4 text-left">Document</th>
                  <th className="py-2 px-4 text-left">Status</th>
                  <th className="py-2 px-4 text-left">Assigned By</th>
                  <th className="py-2 px-4 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {filterDocsByStatus(assignedDocs[reviewUser.userId] || []).map(doc => (
                  <tr key={doc.docName} className="border-b hover:bg-blue-50">
                    <td className="py-2 px-3 flex items-center gap-2">
                      <FileText size={16} className="text-blue-400" />
                      {doc.docName}
                    </td>
                    <td className="py-2 px-3">
                      {doc.status === "verified" ? (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                          <CheckCircle size={12} /> Verified
                        </span>
                      ) : doc.fileUrl ? (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                          <Upload size={12} /> Uploaded
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                          <Clock size={12} /> Pending
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-3">{doc.assignedBy || "-"}</td>
                    <td className="py-2 px-3 flex gap-2">
                      {doc.fileUrl && (
                        <a href={`${ipadr}${doc.fileUrl}`} target="_blank" rel="noreferrer" className="text-blue-600 flex items-center gap-1">
                          <Eye size={14} />
                        </a>
                      )}
                      {doc.fileUrl && doc.status !== "verified" && (
                        <button onClick={() => handleVerify(reviewUser.userId, doc.docName)} className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 flex items-center gap-1 text-xs">
                          <Check size={14} /> 
                        </button>
                      )}
                      <button onClick={() => handleDelete(reviewUser.userId, doc.docName)} className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 flex items-center gap-1 text-xs">
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
